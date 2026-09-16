"""Pure flat-src identity policy; evidence v2: committed bytes in, identity-only bytes out. No I/O."""

from pathlib import PurePosixPath
import re

POLICY = 2
CANONICAL_SHA = "720260c7d8d5096bddbd0cc6d6f90f9f311d809a"
MIGRATION = "alembic/versions/b7f42e9c1a60_initial_items_actions.py"
# Exact service/database/logger identities, never a Python package mapping.
IDENTITY_PATHS = {
    b"goalstats_template_py": {
        ".env.example",
        "docker/compose.local.yml",
        "docker/compose.dev.yml",
        "docs/service/development.md",
        "docs/standard/template.md",
        "scripts/smoke/runtime.py",
        "scripts/validation/certify_workflows.py",
        "tests/fixtures/smoke.py",
    },
    b"goalstats_template": {"src/main.py", "docs/standard/template.md"},
    b"goalstats-template-py": {
        ".env.example",
        "docker/compose.local.yml",
        "docker/compose.dev.yml",
        "docker/compose.test.yml",
        "docs/service/development.md",
        "docs/standard/template.md",
        "scripts/smoke/runtime.py",
        "scripts/tests/test_workflow.py",
        "scripts/validation/certify_workflows.py",
        "scripts/workflow.py",
        "src/settings/base.py",
        "tests/fixtures/smoke.py",
        "tests/unit/schemas/test_domain.py",
    },
    b"GoalStats Template API": {"src/main.py", "docs/standard/template.md"},
    b"template-goalstats-service": {"docs/standard/template.md"},
    b"goalstats-template-${{": {
        ".github/workflows/ci.yml",
        "docs/standard/template.md",
    },
}
TOKENS = tuple(IDENTITY_PATHS)
RESERVED = TOKENS + (
    b"goalstats-template-",
    b"GoalStats.Template",
    b"TemplateDbContext",
)
FACTORY = "main:create_app()"

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
    logger = "goalstats_" + stem.replace("-", "_")
    database = logger + "_py"
    slug = "goalstats-" + stem + "-py"
    require(
        len(database + "_local") <= 63 and len(slug) <= 60,
        "Derived identity too long",
    )
    return dict(
        service=service,
        domain=domain,
        stem=stem,
        logger=logger,
        database=database,
        factory=FACTORY,
        slug=slug,
        api="GoalStats " + domain + " API",
        local=database + "_local",
        dev=database + "_dev",
        test="goalstats_test_runtime",
    )


def validate_path(path):
    require(isinstance(path, str), "Unsafe payload path: " + repr(path))
    require(
        not path.startswith("src/goalstats_") and path != "src/__init__.py",
        "Service package/root package is incompatible with flat src: " + path,
    )
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
    database="goalstats_template_py",
    slug="goalstats-template-py",
    api="GoalStats Template API",
    service="template-goalstats-service",
    logger="goalstats_template",
):
    return {
        "src/main.py": (
            b"def create_app(",
            api.encode(),
            (f'logging.Logger("{logger}"').encode(),
        ),
        "src/composition.py": (
            b"def get_database(",
            b"def get_item_service(",
            b"def get_action_service(",
        ),
        "src/enums/item.py": (b"ItemStatus",),
        "src/enums/action.py": (b"ActionType",),
        "src/exceptions/base.py": (b"DomainError",),
        "src/models/base.py": (b"DeclarativeBase",),
        "src/models/item.py": (b"Item",),
        "src/models/action.py": (b"Action",),
        "src/schemas/base.py": (b"RequestSchema",),
        "src/infra/resources/db.py": (b"class Database", b"def transaction("),
        "src/infra/resources/redis.py": (b"class RedisCache",),
        "src/infra/repositories/item.py": (b"class ItemRepository",),
        "src/infra/repositories/action.py": (b"class ActionRepository",),
        "src/infra/caches/item.py": (b"class ItemCache",),
        "src/infra/caches/action.py": (b"class ActionCache",),
        "src/services/item/item.py": (b"class ItemService",),
        "src/services/item/action.py": (b"class ActionService",),
        "src/routers/item/item.py": (b"def create_items_blueprint(",),
        "src/routers/item/action.py": (b"def create_actions_blueprint(",),
        "src/settings/base.py": ((slug + ":local:v1").encode(),),
        "Dockerfile": (
            b"python:3.12-",
            FACTORY.encode(),
            b"gunicorn",
            b"PYTHONPATH=/app/src",
        ),
        "requirements.txt": tuple(
            x.encode() + b"=="
            for x in [
                "Flask",
                "SQLAlchemy",
                "alembic",
                "redis",
                "flask-smorest",
                "marshmallow",
                "pytest",
                "gunicorn",
            ]
        ),
        "alembic.ini": (b"%(here)s/src",),
        "alembic/env.py": (b"import models", b"from models.base import Base"),
        MIGRATION: (b"b7f42e9c1a60",),
        "docker/compose.local.yml": (
            (database + "_local").encode(),
            (slug + ":runtime").encode(),
            FACTORY.encode(),
        ),
        "docker/compose.dev.yml": (
            (database + "_dev").encode(),
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
            b"--cov=src",
        ),
        "scripts/smoke/runtime.py": (
            (database + "_dev").encode(),
            (slug + ":dev:v1").encode(),
        ),
        "tests/fixtures/smoke.py": ((slug + "-cert-[a-f0-9]+").encode(),),
        ".github/workflows/ci.yml": ((slug[:-3] + "-${{").encode(), b"'3.12'"),
        "docs/standard/template.md": (service.encode(), api.encode(), FACTORY.encode()),
        "pytest.ini": (b"pythonpath = src scripts",),
        "mypy.ini": (b"mypy_path = src",),
        "Makefile": (b"include make/",),
        ".gitignore": (b"__pycache__/",),
        "README.md": (b"Flask", FACTORY.encode()),
        **{
            "make/" + name + ".mk": ()
            for name in ["install", "doctor", "dev", "db", "test", "coverage", "ci"]
        },
    }


def check_flat_content(path, data):
    if path.endswith(".py"):
        require(
            not re.search(rb"(?:from|import)\s+goalstats_[A-Za-z0-9_]+", data),
            "Obsolete service package import: " + path,
        )


def check_anchors(payload, values=None):
    expected = (
        anchors()
        if values is None
        else anchors(
            values["database"],
            values["slug"],
            values["api"],
            values["service"],
            values["logger"],
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
                values["database"].encode(),
                values["logger"].encode(),
                values["slug"].encode(),
                values["api"].encode(),
                values["service"].encode(),
                ("goalstats-" + values["stem"] + "-${{").encode(),
            ],
        )
    )
    pattern = re.compile(b"|".join(map(re.escape, TOKENS)))

    def replace(match):
        token = match.group()
        a, b = match.span()
        require(path in IDENTITY_PATHS[token], "Unexpected identity location: " + path)
        require(
            not (a and re.match(rb"[A-Za-z0-9_]", data[a - 1 : a])),
            "Embedded identity: " + path,
        )
        tail = data[b:]
        if token == b"goalstats_template_py":
            require(
                re.match(rb"_(?:local|dev)(?![A-Za-z0-9_])|_(?=[\"'])", tail),
                "Unexpected database identity: " + path,
            )
        else:
            require(
                not re.match(rb"[A-Za-z0-9_]", tail[:1]), "Embedded identity: " + path
            )
        if token in {
            b"goalstats-template-py",
            b"template-goalstats-service",
            b"goalstats-template-${{",
        }:
            require(
                not (
                    a >= 2
                    and data[a - 1 : a] == b"-"
                    and re.match(rb"[A-Za-z0-9_-]", data[a - 2 : a - 1])
                ),
                "Embedded slug: " + path,
            )
        return replacements[token]

    check_flat_content(path, data)
    result = pattern.sub(replace, data)
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
        new = old  # Flat modules and every other path retain their canonical names.
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
