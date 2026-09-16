import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest.mock import patch
from scaffold_fixtures import Fixture, golden, PAYLOAD


class Scaffold(Fixture, unittest.TestCase):
    def test_preview_write_free(self):
        before = self.snap(self.base)
        p = self.invoke("true")
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertEqual(before, self.snap(self.base))
        self.assertFalse(self.lock.exists())
        self.assertNotIn("PACKAGE=", p.stdout)
        for token in [
            "WRITES=NONE",
            "ITEM_ACTION_TRANSFORMATION=NO",
            "SOURCE_LAYOUT=flat-src",
            "FACTORY_TARGET=main:create_app()",
            "PYTHON_PACKAGE_DIRECTORY_TRANSFORMATION=NO",
            "PATH_TRANSFORMATIONS=0",
            "goalstats-user-py",
            "goalstats_test_runtime",
            "PLANNED_FILES=" + str(len(PAYLOAD)),
        ]:
            self.assertIn(token, p.stdout)

    def test_preview_syscall_write_guard(self):
        code = """import sys,os,runpy

def audit(event,args):
 if event in ('os.mkdir','os.rename','os.remove','os.rmdir','tempfile.mkstemp','tempfile.mkdtemp'):raise AssertionError(event)
 if event=='open' and (args[2] & (os.O_CREAT|os.O_WRONLY|os.O_RDWR)):raise AssertionError('file write')
sys.addaudithook(audit)
sys.argv=['scripts/scaffold-service.py']
runpy.run_path('scripts/scaffold-service.py',run_name='__main__')
"""
        before = self.snap(self.base)
        p = self.cmd(
            self.parent,
            sys.executable,
            "-I",
            "-B",
            "-c",
            code,
            ok=False,
            env={
                **self.env,
                "SERVICE": "goalstats-user-service",
                "DOMAIN": "User",
                "DRY_RUN": "true",
            },
        )
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertEqual(before, self.snap(self.base))

    def test_install_exact_and_git_preservation(self):
        before = [self.s.snapshot(p) for p in (self.parent, self.src, self.dest)]
        p = self.invoke()
        self.assertEqual(p.returncode, 0, p.stdout)
        self.s.verify(self.dest, golden(PAYLOAD), True)
        self.assertEqual(
            before, [self.s.snapshot(p) for p in (self.parent, self.src, self.dest)]
        )
        self.assertFalse(self.marker.exists())
        self.assertFalse(self.lock.exists())
        self.assertEqual(
            self.git(
                self.parent, "ls-tree", "HEAD", "backend/goalstats-user-service"
            ).split()[2],
            self.placeholder,
        )

    def test_detached_attach_and_preview(self):
        self.git(self.dest, "checkout", "--detach", "-q", self.placeholder)
        before = self.snap(self.parent)
        p = self.invoke("true")
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("ATTACH_EXISTING_MASTER", p.stdout)
        self.assertEqual(before, self.snap(self.parent))
        p = self.invoke()
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertEqual(self.git(self.dest, "branch", "--show-current"), "master")

    def test_missing_master(self):
        self.git(self.dest, "checkout", "--detach", "-q", self.placeholder)
        self.git(self.dest, "branch", "-D", "master")
        self.refuse()

    def test_worktree_owner(self):
        self.git(self.dest, "checkout", "--detach", "-q", self.placeholder)
        self.git(
            self.dest, "worktree", "add", "-q", str(self.base / "linked"), "master"
        )
        self.refuse()

    def test_parent_branch(self):
        self.git(self.parent, "checkout", "--detach", "-q")
        self.refuse()

    def test_destination_branch(self):
        self.git(self.dest, "switch", "-c", "wrong")
        self.refuse()

    def test_dirty_parent(self):
        (self.parent / "TODO.md").write_text("preserve")
        self.refuse()

    def test_dirty_source(self):
        (self.src / "README.md").write_text("preserve")
        self.refuse()

    def test_dirty_placeholder(self):
        (self.dest / "README.md").write_text("preserve")
        self.refuse()

    def test_ignored_extra(self):
        (self.dest / "bin").mkdir()
        (self.dest / "bin/private").write_text("preserve")
        self.refuse()

    def test_symlink(self):
        (self.dest / "README.md").unlink()
        (self.dest / "README.md").symlink_to(self.base / "target/README.md")
        self.refuse()

    def test_origin(self):
        self.git(
            self.dest, "remote", "set-url", "origin", "https://invalid.example/other"
        )
        self.refuse()

    def test_source_offpin(self):
        (self.src / "extra").write_text("x")
        self.commit(self.src)
        self.refuse()

    def test_staged_gitlink(self):
        self.git(
            self.parent,
            "update-index",
            "--cacheinfo",
            "160000," + self.placeholder + ",backend/template-goalstats-service",
        )
        self.refuse()

    def test_operation_marker(self):
        (self.dest / ".git").read_text()
        gd = Path(self.git(self.dest, "rev-parse", "--absolute-git-dir"))
        (gd / "MERGE_HEAD").write_text(self.placeholder)
        self.refuse()

    def test_old_marker_preserved(self):
        self.marker.mkdir()
        (self.marker / "recovery-directory").write_text("historical")
        self.refuse()

    def test_lock_refusal(self):
        self.lock.mkdir()
        self.refuse(dry="true")
        self.refuse()

    def test_inputs_and_make_expansion(self):
        for values in [
            {"SERVICE": "$(shell touch OWNED)"},
            {"DOMAIN": "$(shell touch OWNED)"},
            {"DOMAIN": "Team"},
            {"dry": ""},
            {"dry": "TRUE"},
        ]:
            self.refuse(**values)
        self.assertFalse((self.parent / "OWNED").exists())

    def test_registry(self):
        p = self.parent / "config/scaffolds.tsv"
        original = p.read_text()
        for value in [
            original + original,
            original.replace("\tUser", ""),
            original.replace(self.placeholder, "x" * 40),
        ]:
            p.write_text(value)
            self.commit(self.parent)
            self.refuse()

    def test_repeat_dirty_and_committed(self):
        self.assertEqual(self.invoke().returncode, 0)
        for dry in ["true", "false"]:
            self.refuse(dry=dry)
        self.commit(self.dest)
        for dry in ["true", "false"]:
            self.refuse(dry=dry)

    def test_preparation_failure(self):
        before = self.snap(self.dest)
        with patch.object(
            self.s,
            "verify",
            side_effect=lambda path, payload, installed=False: (
                (_ for _ in ()).throw(OSError("prepare failure"))
                if Path(path).name == "prepared"
                else self.s.v.verify(
                    path,
                    {p: (m, self.s.v.blob(d)) for p, (m, d) in payload.items()},
                    installed,
                )
            ),
        ):
            with self.assertRaises(OSError):
                self.s.execute("goalstats-user-service", "User", False)
        self.assertEqual(before, self.snap(self.dest))
        self.assertTrue(self.marker.exists())
        self.assertFalse(self.lock.exists())

    def test_install_failure_and_interruption(self):
        original = self.s.install_file
        calls = []

        def fail(*args):
            if calls:
                raise KeyboardInterrupt()
            calls.append(args[1])
            return original(*args)

        with patch.object(self.s, "install_file", side_effect=fail):
            with self.assertRaises(KeyboardInterrupt):
                self.s.execute("goalstats-user-service", "User", False)
        self.assertTrue(self.marker.exists())
        self.assertTrue((self.marker / "operation.json").exists())
        self.assertIn("complete", (self.marker / "progress.jsonl").read_text())
        self.assertFalse(self.lock.exists())
        self.refuse()

    def test_final_verification_failure(self):
        original = self.s.verify

        def fail(path, payload, installed=False):
            if Path(path) == self.dest and (self.dest / "Dockerfile").exists():
                raise ValueError("final failure")
            return original(path, payload, installed)

        with patch.object(self.s, "verify", side_effect=fail):
            with self.assertRaises(ValueError):
                self.s.execute("goalstats-user-service", "User", False)
        self.assertTrue(self.marker.exists())
        self.assertFalse(self.lock.exists())

    def test_concurrent_edit_preserved(self):
        expected = self.s.preflight("goalstats-user-service", "User")["original"]
        (self.dest / "README.md").write_text("concurrent")
        fd = os.open(self.dest, os.O_RDONLY | os.O_DIRECTORY)
        try:
            with self.assertRaises(ValueError):
                self.s.install_file(fd, "README.md", "100644", b"new", expected)
        finally:
            os.close(fd)
        self.assertEqual((self.dest / "README.md").read_text(), "concurrent")

    def test_concurrent_operations(self):
        # Hold the real owner after lock acquisition; a second process must refuse.
        code = """import importlib.util,time
s=importlib.util.spec_from_file_location('s','scripts/scaffold-service.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
old=m.preflight
count=0
def pause(*a,**k):
 global count
 count+=1
 if count==2:
  print('LOCKED',flush=True);input()
 return old(*a,**k)
m.preflight=pause;m.execute('goalstats-user-service','User',False)
"""
        p = subprocess.Popen(
            [sys.executable, "-I", "-B", "-c", code],
            cwd=self.parent,
            env=self.env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            self.assertEqual(p.stdout.readline().strip(), "LOCKED")
            self.refuse(dry="true")
            self.refuse()
            output = p.communicate(input="\n", timeout=30)[0]
            self.assertEqual(p.returncode, 0, output)
        finally:
            if p.poll() is None:
                p.kill()
                p.communicate()

    def test_offline_no_network_commands(self):
        original = self.s.git
        calls = []

        def checked(repo, *args, **kw):
            calls.append(args[0])
            self.assertNotIn(args[0], ["fetch", "pull", "push", "clone", "ls-remote"])
            return original(repo, *args, **kw)

        with patch.object(self.s, "git", side_effect=checked):
            self.s.execute("goalstats-user-service", "User", False)
        self.assertTrue(calls)
        self.assertEqual(self.s.GIT_ENV["GIT_ALLOW_PROTOCOL"], "")

    def test_missing_object(self):
        oid = self.git(self.src, "rev-parse", "HEAD:README.md")
        gd = Path(self.git(self.src, "rev-parse", "--absolute-git-dir"))
        (gd / "objects" / oid[:2] / oid[2:]).unlink()
        self.refuse()

    def test_strict_extras(self):
        self.assertEqual(self.invoke().returncode, 0)
        for name in [
            "bin/x",
            "obj/x",
            "__pycache__/x",
            ".pytest_cache/x",
            "venv/x",
            ".coverage",
        ]:
            p = self.dest / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("extra")
            with self.assertRaises(ValueError):
                self.s.verify(self.dest, golden(PAYLOAD), True)
            p.unlink()
            if p.parent != self.dest:
                p.parent.rmdir()

    def test_actual_signals_preserve_evidence(self):
        import signal

        code = """import importlib.util,sys
s=importlib.util.spec_from_file_location('s','scripts/scaffold-service.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def pause(*a,**k):
 print('INSTALLING',flush=True);input()
m.install_file=pause;sys.argv=['scripts/scaffold-service.py']
try:m.main()
except RuntimeError:sys.exit(1)
"""
        # One signal per fixture operation; interruption is genuinely delivered by the OS.
        p = subprocess.Popen(
            [sys.executable, "-I", "-B", "-c", code],
            cwd=self.parent,
            env={**self.env, "SERVICE": "goalstats-user-service", "DOMAIN": "User"},
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            self.assertEqual(p.stdout.readline().strip(), "INSTALLING")
            p.send_signal(signal.SIGTERM)
            output = p.communicate(timeout=20)[0]
            self.assertEqual(p.returncode, 1, output)
            self.assertTrue(self.marker.exists())
            self.assertFalse(self.lock.exists())
            self.refuse()
        finally:
            if p.poll() is None:
                p.kill()
                p.communicate()

    def test_resource_namespace_isolation(self):
        out = golden(PAYLOAD)
        text = out["scripts/workflow.py"][1].decode()
        import re

        pattern = re.search(
            r'r"(goalstats-user-py-\(test\|cert\)-\[a-f0-9\]\+)"', text
        ).group(1)
        self.assertTrue(re.fullmatch(pattern, "goalstats-user-py-test-a123"))
        for project in [
            "goalstats-template-py-test-a123",
            "goalstats-team-py-cert-a123",
            "goalstats-user-py-local",
            "goalstats-user-py-test-../x",
        ]:
            self.assertFalse(re.fullmatch(pattern, project))

    def test_symlink_ancestor_during_install(self):
        outside = self.base / "outside"
        outside.mkdir()
        (self.dest / "src").symlink_to(outside, target_is_directory=True)
        fd = os.open(self.dest, os.O_RDONLY | os.O_DIRECTORY)
        try:
            with self.assertRaises(OSError):
                self.s.install_file(fd, "src/x.py", "100644", b"bad", {})
        finally:
            os.close(fd)
        self.assertEqual(list(outside.iterdir()), [])

    def test_destination_mode(self):
        (self.dest / "README.md").chmod(0o755)
        self.refuse()

    def test_duplicate_derived_identity(self):
        p = self.parent / "config/scaffolds.tsv"
        p.write_text(
            p.read_text() + "goalstats-user-service\t" + self.placeholder + "\tTeam\n"
        )
        self.commit(self.parent)
        self.refuse()
