"""Read-only Python child classification; never import or execute child code."""

import os
from pathlib import Path
import sys
import importlib.util

spec = importlib.util.spec_from_file_location(
    "scaffold_service", Path(__file__).with_name("scaffold-service.py")
)
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


def classify(root, service, domain, approved, incomplete=False):
    root = Path(root)
    if incomplete:
        return "INCOMPLETE", "A scaffold operation requires manual review"
    try:
        s.safe_path(root)
        s.operations(root)
        values = s.t.identity(service, domain)
        head = s.text(root, "rev-parse", "HEAD")
        if head == approved:
            original = s.payload(root, approved)
            if set(original) == {"README.md", ".gitignore"}:
                try:
                    s.clean(root)
                    s.verify(root, original, True)
                    return (
                        "PLACEHOLDER",
                        "Approved placeholder; scaffold before runtime/tests",
                    )
                except (ValueError, OSError):
                    pass
        files = {}
        for path in s.t.anchors(
            values["package"], values["slug"], values["api"], values["service"]
        ):
            p = s.safe_path(root / path)
            if not p.is_file():
                return "INVALID", "Missing Python anchor: " + path
            files[path] = ("100644", p.read_bytes())
        s.t.check_anchors(files, values)
        for directory in ["src", "tests", "alembic", "scripts", "docker", "make"]:
            for base, dirs, names in os.walk(root / directory, followlinks=False):
                for name in dirs + names:
                    p = Path(base) / name
                    if p.is_symlink():
                        return "INVALID", "Symlink in application tree"
                    if p.suffix in {".cs", ".csproj", ".sln"}:
                        return "INVALID", "Mixed legacy/Python payload"
                    if p.is_file() and p.suffix in s.t.TEXT_SUFFIXES:
                        if any(token in p.read_bytes() for token in s.t.RESERVED):
                            return "INVALID", "Residual template/legacy identity"
        if any(root.glob("*.sln")) or (root / "global.json").exists():
            return "INVALID", "Legacy runtime files"
        return (
            "SCAFFOLDED",
            "Python structure present; runtime certification and parent integration are separate",
        )
    except (ValueError, OSError, UnicodeError):
        return "INVALID", "Invalid Python/Git contract; existing files preserved"


def main():
    if len(sys.argv) != 2:
        return 2
    path = Path(os.path.abspath(sys.argv[1]))
    service = path.name
    rows = [
        line.split("\t")
        for line in (s.ROOT / "config/scaffolds.tsv").read_text().splitlines()
        if line and not line.startswith("#")
    ]
    matches = [row for row in rows if len(row) == 3 and row[0] == service]
    if len(matches) != 1:
        print("INVALID: service not approved", file=sys.stderr)
        return 2
    _, sha, domain = matches[0]
    marker = s.gitpath(s.ROOT, "team-squared-scaffold-incomplete")
    state, reason = classify(
        path, service, domain, sha, marker.exists() or marker.is_symlink()
    )
    print(f"{service}: {state}: {reason}")
    return 0 if state == "SCAFFOLDED" else 2


if __name__ == "__main__":
    sys.exit(main())
