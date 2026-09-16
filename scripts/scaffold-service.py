"""Offline, identity-only scaffolding with write-free preview and durable failure evidence."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import shutil
import signal
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "backend/template-goalstats-service"


def load(name):
    spec = importlib.util.spec_from_file_location(
        name.replace("-", "_"), Path(__file__).with_name(name + ".py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


t = load("scaffold-transform")
v = load("scaffold-verify")
require = t.require

# Disable optional index writes, lazy fetch, replacement history and external helpers.
GIT_ENV = {k: value for k, value in os.environ.items() if not k.startswith("GIT_")}
GIT_ENV.update(
    GIT_OPTIONAL_LOCKS="0",
    GIT_NO_LAZY_FETCH="1",
    GIT_ALLOW_PROTOCOL="",
    GIT_NO_REPLACE_OBJECTS="1",
    GIT_TERMINAL_PROMPT="0",
)


def git(repo, *args, optional=False):
    p = subprocess.run(
        [
            "git",
            "-c",
            "core.fsmonitor=false",
            "-c",
            "core.untrackedCache=false",
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "submodule.recurse=false",
            "-c",
            "core.logAllRefUpdates=true",
            "-C",
            str(repo),
            *args,
        ],
        env=GIT_ENV,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if p.returncode and not optional:
        raise t.Refusal("Git check failed: " + args[0])
    return p.stdout if not p.returncode else b""


def text(repo, *args, **kw):
    return git(repo, *args, **kw).decode().strip()


def gitpath(repo, name):
    p = Path(text(repo, "rev-parse", "--git-path", name))
    return p if p.is_absolute() else repo / p


def safe_path(path):
    path = Path(os.path.abspath(path))
    # Root is resolved once; user-controlled symlinks below it are never accepted.
    for p in [path, *path.parents]:
        if p == ROOT.parent:
            break
        require(not p.is_symlink(), "Symlink in operation path: " + str(p))
    return path


def operations(repo):
    for name in [
        "MERGE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "rebase-merge",
        "rebase-apply",
        "sequencer",
        "BISECT_START",
    ]:
        p = gitpath(repo, name)
        require(
            not p.exists() and not p.is_symlink(), "Git operation in progress: " + name
        )
    require(
        not text(repo, "for-each-ref", "--format=%(refname)", "refs/replace/"),
        "Replacement history unsupported",
    )
    require(not gitpath(repo, "info/grafts").exists(), "Grafted history unsupported")


def clean(repo):
    operations(repo)
    require(
        not git(
            repo,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "--ignore-submodules=all",
        ),
        "Dirty work preserved: " + str(repo),
    )
    require(
        not git(
            repo,
            "diff",
            "--cached",
            "--name-status",
            "--ignore-submodules=none",
            "HEAD",
        ),
        "Staged changes preserved: " + str(repo),
    )


def tree(repo, commit):
    result = {}
    for row in git(repo, "ls-tree", "-rz", commit).split(b"\0"):
        if not row:
            continue
        meta, name = row.split(b"\t")
        mode, kind, oid = meta.decode().split()
        result[name.decode()] = (mode, kind, oid)
    return result


def payload(repo, commit):
    result = {}
    for path, (mode, kind, oid) in tree(repo, commit).items():
        require(
            kind == "blob" and mode in {"100644", "100755"},
            "Unsupported source entry: " + path,
        )
        result[path] = (mode, git(repo, "cat-file", "blob", oid))
    return result


def snapshot(repo):
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

    return dict(
        head=text(repo, "rev-parse", "HEAD"),
        branch=text(repo, "symbolic-ref", "-q", "HEAD", optional=True),
        refs=git(
            repo, "for-each-ref", "--format=%(refname) %(objectname) %(symref)"
        ).decode(),
        config=git(repo, "config", "--local", "--null", "--list").hex(),
        index=digest(gitpath(repo, "index")),
        pointer=digest(repo / ".git"),
        gitdir=text(repo, "rev-parse", "--absolute-git-dir"),
        reflog=digest(gitpath(repo, "logs/HEAD")),
    )


def metadata(parent_sha):
    entries = tree(ROOT, parent_sha)
    rows = (
        git(
            ROOT,
            "config",
            "--blob",
            parent_sha + ":.gitmodules",
            "--get-regexp",
            r"^submodule\..*\.(path|url)$",
        )
        .decode()
        .splitlines()
    )
    values = {}
    for row in rows:
        key, value = row.split(None, 1)
        require(key not in values, "Duplicate submodule metadata")
        values[key] = value
    result = {}
    for key, path in values.items():
        if not key.endswith(".path"):
            continue
        t.validate_path(path)
        url = values.get(key[:-5] + ".url")
        require(
            path not in result and url and entries.get(path, ("",))[0] == "160000",
            "Invalid submodule mapping",
        )
        result[path] = (entries[path][2], url)
    require(
        set(result) == {p for p, e in entries.items() if e[0] == "160000"},
        "Unregistered gitlink",
    )
    return result


def preflight(service, domain, owned_marker=None):
    values = t.identity(service, domain)
    require(
        text(ROOT, "symbolic-ref", "-q", "HEAD", optional=True) == "refs/heads/master",
        "Parent must be master",
    )
    clean(ROOT)
    gd = safe_path(Path(text(ROOT, "rev-parse", "--absolute-git-dir")))
    marker = gd / "team-squared-scaffold-incomplete"
    for name in ["team-squared-workspace-sync", "team-squared-scaffold-incomplete"]:
        p = gd / name
        require(
            p == owned_marker or (not p.exists() and not p.is_symlink()),
            "Incomplete operation requires manual preservation: " + str(p),
        )
    parent_sha = text(ROOT, "rev-parse", "HEAD")
    links = metadata(parent_sha)
    roles = {}
    for row in (
        git(ROOT, "show", parent_sha + ":config/components.tsv").decode().splitlines()
    ):
        if not row or row.startswith("#"):
            continue
        fields = row.split("\t")
        require(len(fields) == 9, "Invalid component row")
        require(fields[2] not in roles, "Duplicate component")
        roles[fields[2]] = fields[0]
    approvals = {}
    identities = set()
    domains = set()
    for row in (
        git(ROOT, "show", parent_sha + ":config/scaffolds.tsv").decode().splitlines()
    ):
        if not row or row.startswith("#"):
            continue
        fields = row.split("\t")
        require(len(fields) == 3, "Approval requires three columns")
        name, sha, approved_domain = fields
        iv = t.identity(name, approved_domain)
        require(
            len(sha) == 40 and all(c in "0123456789abcdef" for c in sha),
            "Invalid placeholder SHA",
        )
        require(
            name not in approvals and approved_domain.lower() not in domains,
            "Duplicate approval/domain",
        )
        domains.add(approved_domain.lower())
        for value in (iv["logger"], iv["slug"], iv["local"], iv["dev"]):
            require(value not in identities, "Duplicate derived identity")
            identities.add(value)
        path = "backend/" + name
        require(
            path in links and roles.get(path) == "active",
            "Destination not an active registered submodule",
        )
        repo = safe_path(ROOT / path)
        require(
            (repo / ".git").exists(),
            "Uninitialized approved destination; run setup separately",
        )
        git(repo, "cat-file", "-e", sha + "^{commit}")
        approvals[name] = (sha, approved_domain)
    require(
        service in approvals and approvals[service][1] == domain,
        "SERVICE/DOMAIN not approved",
    )
    require(
        roles.get(SOURCE) == "reference" and SOURCE in links,
        "Template must be registered reference",
    )
    dest_path = "backend/" + service
    approved = approvals[service][0]
    require(
        links[dest_path][0] == approved,
        "Parent destination pin differs from placeholder",
    )
    src = safe_path(ROOT / SOURCE)
    dest = safe_path(ROOT / dest_path)
    for repo, path in [(src, SOURCE), (dest, dest_path)]:
        require(
            (repo / ".git").exists() and not (repo / ".git").is_symlink(),
            "Invalid Git administration",
        )
        require(
            Path(text(repo, "rev-parse", "--show-toplevel")).resolve() == repo,
            "Not an independent repository",
        )
        clean(repo)
        require(
            text(repo, "rev-parse", "HEAD") == links[path][0],
            "Off-pin child preserved: " + path,
        )
        require(
            text(repo, "remote", "get-url", "origin") == links[path][1],
            "Noncanonical origin: " + path,
        )
    require(
        text(src, "symbolic-ref", "-q", "HEAD", optional=True)
        in {"", "refs/heads/master"},
        "Template must be master or pinned detached",
    )
    branch = text(dest, "symbolic-ref", "-q", "HEAD", optional=True)
    require(
        branch in {"", "refs/heads/master"},
        "Destination must be master or safely detached",
    )
    for ref in ["refs/heads/master", "refs/remotes/origin/master"]:
        require(
            not text(dest, "symbolic-ref", "-q", ref, optional=True),
            "Master refs must not be symbolic",
        )
        require(
            text(dest, "rev-parse", "--verify", ref) == approved,
            "Existing master/origin/master must equal placeholder",
        )
    owners = (
        git(dest, "worktree", "list", "--porcelain")
        .splitlines()
        .count(b"branch refs/heads/master")
    )
    require(owners == (1 if branch else 0), "Master owned by another worktree")
    original = payload(dest, approved)
    require(
        set(original) == {"README.md", ".gitignore"}
        and all(m == "100644" for m, d in original.values()),
        "Invalid placeholder tree",
    )
    verify(dest, original, True)
    source = payload(src, links[SOURCE][0])
    expected, mapping = t.plan(source, service, domain)
    return dict(
        values=values,
        gd=gd,
        marker=marker,
        src=src,
        dest=dest,
        original=original,
        expected=expected,
        mapping=mapping,
        source_sha=links[SOURCE][0],
        parent_sha=parent_sha,
        branch=branch,
        snapshots=[snapshot(p) for p in (ROOT, src, dest)],
    )


def verify(path, payload, installed=False):
    return v.verify(
        path,
        {p: (mode, v.blob(data)) for p, (mode, data) in payload.items()},
        installed,
    )


def same(a, b):
    require(
        a["snapshots"] == b["snapshots"] and a["expected"] == b["expected"],
        "State changed during preparation",
    )


def report(state, dry):
    i = state["values"]
    for key, value in [
        ("SERVICE", i["service"]),
        ("DOMAIN", i["domain"]),
        ("TEMPLATE_SHA", state["source_sha"]),
        ("DESTINATION_SHA", state["snapshots"][2]["head"]),
        ("SOURCE_LAYOUT", "flat-src"),
        ("FACTORY_TARGET", i["factory"]),
        ("PYTHON_PACKAGE_DIRECTORY_TRANSFORMATION", "NO"),
        ("PATH_TRANSFORMATIONS", sum(a != b for a, b in state["mapping"].items())),
        ("RUNTIME_SLUG", i["slug"]),
        ("API_TITLE", i["api"]),
        ("DATABASE_LOCAL", i["local"]),
        ("DATABASE_DEV", i["dev"]),
        ("DATABASE_TEST", i["test"]),
        ("CACHE_PREFIX", i["slug"] + ":<env>:v1"),
        ("PLANNED_FILES", len(state["expected"])),
        ("BRANCH_ACTION", "NONE" if state["branch"] else "ATTACH_EXISTING_MASTER"),
        ("ITEM_ACTION_TRANSFORMATION", "NO"),
        ("WRITES", "NONE" if dry else "UNSTAGED_PAYLOAD"),
    ]:
        print(f"{key}={value}")


def sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def durable(path, data):
    with path.open("xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    path.chmod(0o600)
    sync_directory(path.parent)


def attach(state):
    dest = state["dest"]
    before = snapshot(dest)
    log = gitpath(dest, "logs/HEAD")
    old = log.read_bytes() if log.exists() else b""
    git(
        dest,
        "symbolic-ref",
        "-m",
        "scaffold: attach approved destination to master",
        "HEAD",
        "refs/heads/master",
    )
    after = snapshot(dest)
    require(after["branch"] == "refs/heads/master", "Attachment failed")
    for key in ["head", "refs", "index", "pointer", "gitdir"]:
        require(
            after[key] == before[key], "Git identity changed during attachment: " + key
        )

    def config(raw):
        result = {}
        for row in bytes.fromhex(raw).split(b"\0"):
            if row:
                k, _, value = row.partition(b"\n")
                result.setdefault(k, []).append(value)
        return result

    a, b = config(before["config"]), config(after["config"])
    key = b"branch.master.vscode-merge-base"
    if key not in a and b.get(key) == [b"origin/master"]:
        del b[key]
    require(a == b, "Unexpected config change during attachment")
    new = log.read_bytes()
    require(new.startswith(old), "Attachment rewrote reflog")
    extra = new[len(old) :].splitlines()
    require(len(extra) == 1, "Unexpected attachment reflog entries")
    fields, sep, message = extra[0].partition(b"\t")
    require(
        fields.split()[:2] == [before["head"].encode()] * 2
        and message == b"scaffold: attach approved destination to master",
        "Unexpected attachment reflog",
    )


def install_file(rootfd, path, mode, data, original):
    """Descriptor-relative traversal; no directory or destination symlink following."""
    parts = path.split("/")
    fd = os.dup(rootfd)
    try:
        for part in parts[:-1]:
            try:
                os.mkdir(part, 0o755, dir_fd=fd)
                os.fsync(fd)
            except FileExistsError:
                pass
            child = os.open(
                part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd
            )
            os.close(fd)
            fd = child
        name = parts[-1]
        try:
            current = os.open(
                name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd
            )
        except FileNotFoundError:
            require(path not in original, "Placeholder disappeared before replacement")
        else:
            with os.fdopen(current, "rb") as f:
                info = os.fstat(f.fileno())
                require(
                    path in original
                    and stat.S_ISREG(info.st_mode)
                    and stat.S_IMODE(info.st_mode) == 0o644
                    and f.read() == original[path][1],
                    "Concurrent destination edit preserved: " + path,
                )
        tmp = ".scaffold-" + secrets.token_hex(12)
        out = os.open(
            tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd
        )
        try:
            with os.fdopen(out, "wb") as f:
                f.write(data)
                os.fchmod(f.fileno(), 0o755 if mode == "100755" else 0o644)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, name, src_dir_fd=fd, dst_dir_fd=fd)
            os.fsync(fd)
        finally:
            try:
                os.unlink(tmp, dir_fd=fd)
            except FileNotFoundError:
                pass
    finally:
        os.close(fd)


def execute(service, domain, dry):
    state = preflight(service, domain)
    lock = state["gd"] / "team-squared-scaffold-v2.lock"
    require(not lock.exists() and not lock.is_symlink(), "Scaffold lock exists")
    if dry:
        same(state, preflight(service, domain))
        require(
            not lock.exists() and not lock.is_symlink(), "Scaffold began during preview"
        )
        report(state, True)
        return
    try:
        lock.mkdir(mode=0o700)
    except FileExistsError:
        raise t.Refusal("Scaffold lock exists") from None
    marker = state["marker"]
    phase = "revalidation"
    started = False
    try:
        same(state, preflight(service, domain))
        marker.mkdir(mode=0o700)
        started = True
        sync_directory(state["gd"])
        info = dict(
            policy_version=2,
            service=service,
            domain=domain,
            source_sha=state["source_sha"],
            parent_sha=state["parent_sha"],
            snapshots=state["snapshots"],
            mapping=state["mapping"],
            manifest={p: [m, v.blob(d)] for p, (m, d) in state["expected"].items()},
        )
        durable(marker / "operation.json", (json.dumps(info, indent=2) + "\n").encode())
        original = marker / "original"
        original.mkdir(mode=0o700)
        for p, (m, d) in state["original"].items():
            durable(original / p, d)
        prepared = marker / "prepared"
        prepared.mkdir(mode=0o700)
        phase = "preparation"
        for p, (mode, data) in state["expected"].items():
            f = prepared / p
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(data)
            f.chmod(0o755 if mode == "100755" else 0o644)
        verify(prepared, state["expected"])
        same(state, preflight(service, domain, marker))
        phase = "master attachment"
        if not state["branch"]:
            attach(state)
        attached = preflight(service, domain, marker)
        require(
            attached["snapshots"][:2] == state["snapshots"][:2],
            "Parent/source changed during attachment",
        )
        durable(
            marker / "installation.json", json.dumps(attached["snapshots"]).encode()
        )
        durable(marker / "progress.jsonl", b"")
        rootfd = os.open(state["dest"], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            for p, (mode, data) in state["expected"].items():
                phase = p
                with (marker / "progress.jsonl").open("ab") as log:
                    log.write((json.dumps({"begin": p}) + "\n").encode())
                    log.flush()
                    os.fsync(log.fileno())
                    install_file(rootfd, p, mode, data, state["original"])
                    log.write((json.dumps({"complete": p}) + "\n").encode())
                    log.flush()
                    os.fsync(log.fileno())
            phase = "final verification"
            opened = os.fstat(rootfd)
            current = state["dest"].lstat()
            require(
                stat.S_ISDIR(current.st_mode)
                and (opened.st_dev, opened.st_ino) == (current.st_dev, current.st_ino),
                "Destination directory replaced",
            )
            verify(state["dest"], state["expected"], True)
        finally:
            os.close(rootfd)
        require(
            [snapshot(p) for p in (ROOT, state["src"], state["dest"])]
            == attached["snapshots"],
            "Git identity changed during installation",
        )
        for p in (ROOT, state["src"], state["dest"]):
            operations(p)
        shutil.rmtree(marker)
        started = False
        sync_directory(state["gd"])
        report(state, False)
        print(
            "Scaffold complete. Files unstaged; child HEAD and parent gitlink unchanged. Runtime certification not performed."
        )
    except BaseException:
        if started:
            durable(
                marker / ("failure-" + secrets.token_hex(4) + ".json"),
                json.dumps({"phase": phase, "automatic_rollback": False}).encode(),
            )
            print(
                "Scaffold INCOMPLETE at "
                + phase
                + ". Preserve partial state; evidence: "
                + str(marker),
                file=sys.stderr,
            )
        raise
    finally:
        lock.rmdir()


def main():
    require(sys.version_info[:2] == (3, 12), "Python 3.12 is required")
    require(
        len(sys.argv) == 1, "Use SERVICE, DOMAIN and DRY_RUN; no positional arguments"
    )
    dry = os.environ.get("DRY_RUN", "false")
    require(dry in {"true", "false"}, "DRY_RUN must be true or false")

    def interrupted(signum, frame):
        raise RuntimeError("Interrupted by signal " + str(signum))

    for sig in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, interrupted)
    execute(os.environ.get("SERVICE", ""), os.environ.get("DOMAIN", ""), dry == "true")


if __name__ == "__main__":
    try:
        main()
    except t.Refusal as error:
        print("Scaffold refused: " + str(error), file=sys.stderr)
        sys.exit(2)
    except (OSError, RuntimeError, UnicodeError, ValueError) as error:
        print("Scaffold failed: " + str(error), file=sys.stderr)
        sys.exit(1)
