"""Read-only IDE profile tooling checks; no providers or child code execution."""

import ast
import json
import unittest

from scaffold_fixtures import IDE_PAYLOAD, PAYLOAD, load

t = load("scaffold-transform")


class IDETooling(unittest.TestCase):
    def test_certified_portable_json(self):
        for path in t.PORTABLE_IDE_FILES:
            t.validate_ide_json(path, IDE_PAYLOAD[path][1])

    def test_absolute_paths_rejected(self):
        for value in (
            "/Users/person/python",
            "C:\\Users\\person\\python.exe",
            "~/private/env",
            "file:///Users/person/python",
            "${env:HOME}/python",
            "${userHome}/python",
            "${workspaceFolder}" + "\\" + ".host-sessions" + "\\" + "old/test.env",
            "${workspaceFolder}/.host-sessions/old/test.env",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                t.validate_ide_json(
                    ".vscode/settings.json", json.dumps({"path": value}).encode()
                )

    def test_credentials_and_embedded_provider_env_rejected(self):
        for data in (
            {"password": "private"},
            {"apiKey": "private"},
            {"url": "redis://private/0"},
            {"env": {"DATABASE_URL": "private"}},
        ):
            with self.subTest(data=data), self.assertRaises(ValueError):
                t.validate_ide_json(".vscode/launch.json", json.dumps(data).encode())

    def test_malformed_json_rejected(self):
        for data in (b"{", b"[]", b"null"):
            with self.subTest(data=data), self.assertRaises(ValueError):
                t.validate_ide_json(".vscode/settings.json", data)

    def test_direct_entrypoint_preserves_factory_and_single_construction(self):
        baseline = ast.parse(PAYLOAD["src/main.py"][1])
        current = ast.parse(IDE_PAYLOAD["src/main.py"][1])

        def factory(tree):
            return next(
                n
                for n in tree.body
                if isinstance(n, ast.FunctionDef) and n.name == "create_app"
            )

        self.assertEqual(ast.dump(factory(baseline)), ast.dump(factory(current)))
        direct = next(
            n
            for n in current.body
            if isinstance(n, ast.FunctionDef) and n.name == "development_main"
        )
        calls = [
            n
            for n in ast.walk(direct)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == "create_app"
        ]
        self.assertEqual(len(calls), 1)
        run = next(
            n
            for n in ast.walk(direct)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr == "run"
        )
        kwargs = {
            k.arg: ast.literal_eval(k.value) for k in run.keywords if k.arg != "port"
        }
        self.assertEqual(
            kwargs,
            {
                "host": "127.0.0.1",
                "debug": False,
                "use_debugger": False,
                "use_reloader": False,
                "load_dotenv": False,
            },
        )

    def test_business_schema_migration_and_dependencies_unchanged(self):
        for path in PAYLOAD:
            if (
                path.startswith(
                    (
                        "src/models/",
                        "src/routers/",
                        "src/schemas/",
                        "src/services/",
                        "src/infra/",
                        "alembic/",
                    )
                )
                or path == "requirements.txt"
            ):
                self.assertEqual(IDE_PAYLOAD[path], PAYLOAD[path], path)

    def test_owned_session_consumers_and_no_default_test_or_dev_publication(self):
        for path in ("tests/fixtures/database.py", "tests/fixtures/redis.py"):
            self.assertIn(b"owned_test_config()", IDE_PAYLOAD[path][1])
        for path in ("docker/compose.dev.yml", "docker/compose.test.yml"):
            expected = PAYLOAD[path][1].replace(b'OPENAPI_ENABLED: "true"', b'OPENAPI_ENABLED: ${OPENAPI_ENABLED:-true}').replace(b'LOG_LEVEL: INFO', b'LOG_LEVEL: ${LOG_LEVEL:-INFO}\n      CACHE_TTL_SECONDS: ${CACHE_TTL_SECONDS:-300}')
            self.assertEqual(IDE_PAYLOAD[path][1], expected)
        ownership = IDE_PAYLOAD["scripts/test_ownership.py"][1]
        for token in (
            b"TEST_SESSION_MANIFEST",
            b"fcntl.LOCK_EX",
            b"com.docker.compose.project",
            b"com.docker.compose.service",
            b"HostPort",
            b"Tmpfs",
            b'manifest["containers"]',
        ):
            self.assertIn(token, ownership)

    def test_profile_guard_refuses_removed_ownership_call(self):
        data = dict(IDE_PAYLOAD)
        mode, body = data["tests/fixtures/redis.py"]
        data["tests/fixtures/redis.py"] = (
            mode,
            body.replace(b"owned_test_config()", b"pass"),
        )
        with self.assertRaises(ValueError):
            t.plan(data, "goalstats-user-service", "User")

    def test_host_loader_is_service_neutral_and_app_launch_needs_no_env(self):
        loader = IDE_PAYLOAD["src/settings/host.py"][1]
        for token in t.TOKENS:
            self.assertNotIn(token, loader)
        launch = json.loads(IDE_PAYLOAD[".vscode/launch.json"][1])
        app = next(c for c in launch["configurations"] if "program" in c)
        self.assertNotIn("envFile", app)
        self.assertNotIn("env", app)
        self.assertNotIn(
            "envFile", next(c for c in launch["configurations"] if "module" in c)
        )
        for key, value in (
            ("envFile", "${workspaceFolder}/.env.host.local"),
            ("env", {"FLASK_DEBUG": "0"}),
        ):
            modified = json.loads(json.dumps(launch))
            modified["configurations"][0][key] = value
            payload = dict(IDE_PAYLOAD)
            payload[".vscode/launch.json"] = ("100644", json.dumps(modified).encode())
            with self.assertRaises(ValueError):
                t.plan(payload, "goalstats-user-service", "User")


    def test_canonical_schema_and_private_file_rejection(self):
        self.assertNotIn(".env.example", IDE_PAYLOAD)
        for path in (".env.local", ".env.test", ".env.example", ".env.host.local", ".host-sessions/x/manifest.json"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                t.validate_path(path)
        schema = IDE_PAYLOAD["src/settings/environment.py"][1]
        self.assertIn(b"LOCAL_KEYS", schema)
        self.assertIn(b"def test_policy(", schema)
        values = t.identity("goalstats-user-service", "User")
        transformed = t.transform(schema, values, "src/settings/environment.py")
        self.assertIn(b'DATABASE = "goalstats_user_py"', transformed)
        with self.assertRaises(ValueError):
            t.transform(b'OTHER = "goalstats_template_py"\n', values, "src/settings/environment.py")
        ownership = IDE_PAYLOAD["scripts/test_ownership.py"][1]
        self.assertIn(b"def owned_test_config(", ownership)
        self.assertIn(b"manifest = verify_host_session(values)", ownership)
