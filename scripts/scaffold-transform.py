"""Pure policy v2: committed bytes in, identity-only bytes out. No I/O."""

from pathlib import PurePosixPath
import re

POLICY = 2
CANONICAL_SHA = "f4e2a94371dd894ffae70eee818f51f92179d183"
MIGRATION = "alembic/versions/b7f42e9c1a60_initial_items_actions.py"
TOKENS = (
    b"goalstats_template",
    b"goalstats-template-py",
    b"GoalStats Template API",
    b"template-goalstats-service",
)
RESERVED = TOKENS + (
    b"goalstats-template-",
    b"GoalStats.Template",
    b"TemplateDbContext",
)
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".yml",
    ".yaml",
    ".json",
    ".ini",
    ".toml",
    ".mk",
    ".sh",
    ".txt",
    ".mako",
}
TEXT_NAMES = {
    "Dockerfile",
    "Makefile",
    ".gitignore",
    ".dockerignore",
    ".env.example",
    ".gitkeep",
}


class Refusal(ValueError):
    pass


def require(value, message):
    if not value:
        raise Refusal(message)


def identity(service, domain):
    require(
        isinstance(service, str)
        and re.fullmatch(r"goalstats-[a-z0-9]+(?:-[a-z0-9]+)*-service", service),
        "Invalid SERVICE",
    )
    require(
        isinstance(domain, str)
        and 2 <= len(domain) <= 15
        and re.fullmatch(r"[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)*", domain)
        and domain != "Template",
        "Invalid DOMAIN",
    )
    stem = service[len("goalstats-") : -len("-service")]
    require(stem != "template", "Template cannot be a destination")
    package = "goalstats_" + stem.replace("-", "_")
    slug = "goalstats-" + stem + "-py"
    require(
        len(package + "_py_local") <= 63 and len(slug) <= 60,
        "Derived identity too long",
    )
    return dict(
        service=service,
        domain=domain,
        stem=stem,
        package=package,
        slug=slug,
        api="GoalStats " + domain + " API",
        local=package + "_py_local",
        dev=package + "_py_dev",
        test="goalstats_test_runtime",
    )


def validate_path(path):
    require(
        isinstance(path, str)
        and re.fullmatch(r"[A-Za-z0-9._/-]+", path)
        and len(path.encode()) <= 900
        and not path.startswith(("/", "-")),
        "Unsafe payload path: " + repr(path),
    )
    for part in path.split("/"):
        low = part.lower()
        require(
            part not in {"", ".", ".."} and not part.endswith(".") and len(part) <= 255,
            "Unsafe payload path: " + path,
        )
        require(
            not re.fullmatch(r"(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", low),
            "Reserved device path: " + path,
        )
        require(
            low
            not in {
                ".git",
                "bin",
                "obj",
                "__pycache__",
                ".pytest_cache",
                ".mypy_cache",
                ".ruff_cache",
                ".venv",
                "venv",
                "coverage",
                "htmlcov",
                "testresults",
                "artifacts",
                "logs",
                "pgdata",
                "postgres-data",
                "redis-data",
            },
            "Forbidden payload artifact: " + path,
        )
        require(
            not (low.startswith(".env") and path != ".env.example")
            and not low.startswith(".coverage"),
            "Forbidden environment/coverage payload: " + path,
        )
    require(
        PurePosixPath(path).suffix.lower()
        not in {
            ".cs",
            ".csproj",
            ".sln",
            ".pyc",
            ".pyo",
            ".sqlite",
            ".sqlite3",
            ".db",
            ".log",
            ".dump",
            ".rdb",
            ".aof",
        },
        "Forbidden payload type: " + path,
    )
    require(
        PurePosixPath(path).name
        not in {"pyproject.toml", "uv.lock", "poetry.lock", "Pipfile", "Pipfile.lock"}
        and not (
            PurePosixPath(path).name.startswith("requirements")
            and path != "requirements.txt"
        ),
        "Unsupported dependency file: " + path,
    )


def collision_check(paths):
    seen = {}
    for path in paths:
        validate_path(path)
        parts = path.split("/")
        for n in range(1, len(parts) + 1):
            current = "/".join(parts[:n])
            kind = "file" if n == len(parts) else "directory"
            old = seen.get(current.lower())
            require(
                not old or (old == (current, kind) and kind == "directory"),
                "Path/case collision: " + path,
            )
            seen[current.lower()] = (current, kind)


def anchors(
    package="goalstats_template",
    slug="goalstats-template-py",
    api="GoalStats Template API",
    service="template-goalstats-service",
):
    p = "src/" + package + "/"
    return {
        p + "__init__.py": (b"create_app",),
        p + "main.py": (b"def create_app(", api.encode()),
        p + "composition.py": (package.encode(),),
        p + "models/base.py": (b"DeclarativeBase",),
        p + "models/item.py": (b"Item",),
        p + "models/action.py": (b"Action",),
        p + "settings/base.py": ((slug + ":local:v1").encode(),),
        "Dockerfile": (
            b"python:3.12-",
            (package + ":create_app()").encode(),
            b"gunicorn",
        ),
        "requirements.txt": (
            b"Flask==",
            b"SQLAlchemy==",
            b"alembic==",
            b"redis==",
            b"flask-smorest==",
            b"marshmallow==",
            b"pytest==",
            b"gunicorn==",
        ),
        "alembic.ini": (b"alembic",),
        "alembic/env.py": (package.encode(),),
        MIGRATION: (b"b7f42e9c1a60",),
        "docker/compose.local.yml": (
            (package + "_py_local").encode(),
            (slug + ":runtime").encode(),
            (package + ":create_app()").encode(),
        ),
        "docker/compose.dev.yml": (
            (package + "_py_dev").encode(),
            (slug + ":runtime").encode(),
        ),
        "docker/compose.test.yml": (
            b"goalstats_test_runtime",
            (slug + ":tooling").encode(),
        ),
        "scripts/workflow.py": (
            (slug + "-(test|cert)-[a-f0-9]+").encode(),
            (slug + "-tool-").encode(),
            (slug + ":tooling").encode(),
        ),
        "scripts/smoke/runtime.py": (
            (package + "_py_dev").encode(),
            (slug + ":dev:v1").encode(),
        ),
        "tests/fixtures/smoke.py": ((slug + "-cert-[a-f0-9]+").encode(),),
        ".github/workflows/ci.yml": ((slug[:-3] + "-${{").encode(), b"'3.12'"),
        "docs/standard/template.md": (service.encode(), api.encode()),
        "Makefile": (b"include make/",),
        ".gitignore": (b"__pycache__/",),
        "README.md": (b"Flask",),
        **{
            "make/" + name + ".mk": ()
            for name in ["install", "doctor", "dev", "db", "test", "coverage", "ci"]
        },
    }


def check_anchors(payload, values=None):
    expected = (
        anchors()
        if values is None
        else anchors(
            values["package"], values["slug"], values["api"], values["service"]
        )
    )
    for path, tokens in expected.items():
        require(
            path in payload and all(t in payload[path][1] for t in tokens),
            "Missing Python anchor: " + path,
        )


def transform(data, values, path):
    replacements = dict(
        zip(
            TOKENS,
            [
                values["package"].encode(),
                values["slug"].encode(),
                values["api"].encode(),
                values["service"].encode(),
            ],
        )
    )
    pattern = re.compile(b"|".join(map(re.escape, TOKENS)))

    def replace(match):
        token = match.group()
        a, b = match.span()
        require(
            not (a and re.match(rb"[A-Za-z0-9_]", data[a - 1 : a])),
            "Embedded identity: " + path,
        )
        tail = data[b:]
        if token == b"goalstats_template" and tail.startswith(b"_py_"):
            pass  # Approved database prefix, including its runtime f-string constructor.
        else:
            require(
                not re.match(rb"[A-Za-z0-9_]", tail[:1]), "Embedded identity: " + path
            )
        if token in {b"goalstats-template-py", b"template-goalstats-service"}:
            require(
                not (
                    a >= 2
                    and data[a - 1 : a] == b"-"
                    and re.match(rb"[A-Za-z0-9_-]", data[a - 2 : a - 1])
                ),
                "Embedded slug: " + path,
            )
        return replacements[token]

    result = pattern.sub(replace, data)
    if path == ".github/workflows/ci.yml":
        result = result.replace(
            b"goalstats-template-${{", ("goalstats-" + values["stem"] + "-${{").encode()
        )
    require(not any(t in result for t in RESERVED), "Residual identity: " + path)
    return result


def plan(payload, service, domain):
    values = identity(service, domain)
    collision_check(payload)
    check_anchors(payload)
    result, mapping = {}, {}
    for old, (mode, data) in payload.items():
        require(
            mode in {"100644", "100755"} and isinstance(data, bytes),
            "Unsupported Git mode/blob: " + old,
        )
        new = (
            old.replace("src/goalstats_template/", "src/" + values["package"] + "/", 1)
            if old.startswith("src/goalstats_template/")
            else old
        )
        require(
            not any(t.decode() in new for t in RESERVED),
            "Residual path identity: " + old,
        )
        if (
            PurePosixPath(old).suffix in TEXT_SUFFIXES
            or PurePosixPath(old).name in TEXT_NAMES
        ):
            try:
                data.decode("utf-8-sig")
            except UnicodeDecodeError:
                raise Refusal("Invalid UTF-8: " + old) from None
            require(b"\0" not in data, "NUL in text: " + old)
            transformed = transform(data, values, old)
        else:
            require(
                not any(t in data for t in RESERVED) and new == old,
                "Identity in opaque file: " + old,
            )
            transformed = data
        if old in {"requirements.txt", MIGRATION, "Makefile"} or old.startswith(
            "make/"
        ):
            require(transformed == data, "Protected file changed: " + old)
        mapping[old] = new
        result[new] = (mode, transformed)
    collision_check(mapping.values())
    check_anchors(result, values)
    return result, mapping
