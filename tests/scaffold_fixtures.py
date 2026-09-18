"""Disposable real-Git fixtures; canonical bytes are read, never edited."""

import hashlib
import importlib.util
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA = "720260c7d8d5096bddbd0cc6d6f90f9f311d809a"


def load(name):
    spec = importlib.util.spec_from_file_location(
        name.replace("-", "_"), ROOT / "scripts" / (name + ".py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def canonical():
    repo = ROOT / "backend/template-goalstats-service"
    result = {}
    for row in subprocess.check_output(
        ["git", "-C", str(repo), "ls-tree", "-rz", SHA]
    ).split(b"\0"):
        if row:
            meta, p = row.split(b"\t")
            mode, kind, oid = meta.decode().split()
            result[p.decode()] = (
                mode,
                subprocess.check_output(
                    ["git", "-C", str(repo), "cat-file", "blob", oid]
                ),
            )
    return result


PAYLOAD = canonical()


def golden(payload, stem="user", domain="User"):
    result = {}
    for p, (m, d) in payload.items():
        name = p
        for old, new in [
            (b"goalstats_template", ("goalstats_" + stem.replace("-", "_")).encode()),
            (b"goalstats-template-py", ("goalstats-" + stem + "-py").encode()),
            (b"GoalStats Template API", ("GoalStats " + domain + " API").encode()),
            (
                b"template-goalstats-service",
                ("goalstats-" + stem + "-service").encode(),
            ),
        ]:
            d = d.replace(old, new)
        if p in {".github/workflows/ci.yml", "docs/standard/template.md"}:
            d = d.replace(
                b"goalstats-template-${{", ("goalstats-" + stem + "-${{").encode()
            )
        result[name] = (m, d)
    return result


class Fixture:
    payload = PAYLOAD

    def cmd(self, cwd, *args, ok=True, env=None):
        p = subprocess.run(
            args,
            cwd=cwd,
            env=env or self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if ok:
            self.assertEqual(p.returncode, 0, p.stdout)
        return p

    def git(self, cwd, *args):
        return self.cmd(cwd, "git", *args).stdout.strip()

    def commit(self, repo):
        self.git(repo, "add", "-A")
        self.git(repo, "commit", "-qm", "fixture")
        return self.git(repo, "rev-parse", "HEAD")

    def init(self, name):
        p = self.base / name
        p.mkdir()
        self.git(p, "init", "-q", "-b", "master")
        return p

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="python-scaffold-test-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.env = {
            **os.environ,
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_ALLOW_PROTOCOL": "file",
            "GIT_OPTIONAL_LOCKS": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
            "GIT_AUTHOR_NAME": "Fixture",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "Fixture",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
        }
        for k in [
            "SERVICE",
            "DOMAIN",
            "DRY_RUN",
            "MAKEFLAGS",
            "MFLAGS",
            "MAKEOVERRIDES",
        ]:
            self.env.pop(k, None)
        source = self.init("source")
        for p, (m, d) in self.payload.items():
            f = source / p
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(d)
            f.chmod(0o755 if m == "100755" else 0o644)
        self.source_sha = self.commit(source)
        target = self.init("target")
        (target / "README.md").write_text("# placeholder\n")
        (target / ".gitignore").write_text("bin/\n.env\n")
        self.placeholder = self.commit(target)
        self.parent = self.init("parent")
        (self.parent / "scripts").mkdir()
        (self.parent / "config").mkdir()
        for p in (ROOT / "scripts").glob("*"):
            if p.is_file():
                shutil.copy2(p, self.parent / "scripts" / p.name)
        shutil.copy2(ROOT / "Makefile", self.parent / "Makefile")
        (self.parent / "config/components.tsv").write_text(
            "reference\tservice-template\tbackend/template-goalstats-service\tnone\tnone\tnone\tnone\tnone\tnone\nactive\tuser-service\tbackend/goalstats-user-service\tuser-service\tpending\tpending\tpending\tpending\tpending\n"
        )
        (self.parent / "config/scaffolds.tsv").write_text(
            "goalstats-user-service\t" + self.placeholder + "\tUser\n"
        )
        self.git(
            self.parent,
            "submodule",
            "add",
            "-q",
            str(source),
            "backend/template-goalstats-service",
        )
        self.git(
            self.parent,
            "submodule",
            "add",
            "-q",
            str(target),
            "backend/goalstats-user-service",
        )
        self.parent_sha = self.commit(self.parent)
        self.src = self.parent / "backend/template-goalstats-service"
        self.dest = self.parent / "backend/goalstats-user-service"
        self.marker = self.parent / ".git/team-squared-scaffold-incomplete"
        self.lock = self.parent / ".git/team-squared-scaffold-v2.lock"
        self.s = load("scaffold-service")
        self.s.ROOT = self.parent

    def invoke(self, dry="false", **values):
        return self.cmd(
            self.parent,
            "make",
            "scaffold-service",
            "SERVICE=" + values.get("SERVICE", "goalstats-user-service"),
            "DOMAIN=" + values.get("DOMAIN", "User"),
            "DRY_RUN=" + dry,
            ok=False,
        )

    def snap(self, root):
        result = {}
        for base, dirs, files in os.walk(root, followlinks=False):
            for name in dirs + files:
                p = Path(base) / name
                r = str(p.relative_to(root))
                result[r] = (
                    p.lstat().st_mode,
                    os.readlink(p)
                    if p.is_symlink()
                    else p.read_bytes()
                    if p.is_file()
                    else None,
                )
        return result

    def refuse(self, **kw):
        before = self.snap(self.parent)
        p = self.invoke(**kw)
        self.assertNotEqual(p.returncode, 0, p.stdout)
        self.assertEqual(before, self.snap(self.parent))
        return p


IDE_DELTA_SHA256 = "8641f4e0c7e6cab78e11650470ff024b712ca5072588800e97fc1f404a99764b"


def ide_payload():
    """Frozen Prompt-1 delta over the approved baseline, never mutable template files."""
    patch = ROOT / "tests/ide-template-delta.patch"
    if hashlib.sha256(patch.read_bytes()).hexdigest() != IDE_DELTA_SHA256:
        raise ValueError(
            "Certified IDE fixture delta changed; review before updating its digest"
        )
    with tempfile.TemporaryDirectory(prefix="ide-payload-") as directory:
        root = Path(directory)
        for name, (mode, data) in PAYLOAD.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            path.chmod(0o755 if mode == "100755" else 0o644)
        subprocess.run(
            ["git", "apply", "--no-index", "--unidiff-zero", str(patch)],
            cwd=root,
            check=True,
            capture_output=True,
        )
        return {
            path.relative_to(root).as_posix(): (
                "100755" if path.stat().st_mode & 0o111 else "100644",
                path.read_bytes(),
            )
            for path in root.rglob("*")
            if path.is_file()
        }


IDE_PAYLOAD = ide_payload()
