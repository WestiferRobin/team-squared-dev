import unittest
from scaffold_fixtures import PAYLOAD, golden, load

t = load("scaffold-transform")


class Transformer(unittest.TestCase):
    def test_canonical_independent_golden(self):
        output, mapping = t.plan(PAYLOAD, "goalstats-user-service", "User")
        self.assertEqual(output, golden(PAYLOAD))
        self.assertEqual(len(output), len(PAYLOAD))
        self.assertEqual(
            sum(a != b for a, b in mapping.items()),
            0,
        )

    def test_multiword(self):
        result, _ = t.plan(PAYLOAD, "goalstats-player-stats-service", "PlayerStats")
        self.assertEqual(result, golden(PAYLOAD, "player-stats", "PlayerStats"))

    def test_invalid_inputs(self):
        for service, domain in [
            ("bad", "User"),
            ("goalstats-user-service", "user"),
            ("goalstats-user-service", "Template"),
            ("goalstats-template-service", "User"),
            ("goalstats-user-service", "$(shell touch x)"),
            ("goalstats-" + "a" * 70 + "-service", "User"),
        ]:
            with (
                self.subTest(service=service, domain=domain),
                self.assertRaises(ValueError),
            ):
                t.identity(service, domain)

    def test_every_anchor_required(self):
        for p in t.anchors():
            data = dict(PAYLOAD)
            del data[p]
            with self.subTest(path=p), self.assertRaises(ValueError):
                t.plan(data, "goalstats-user-service", "User")

    def test_exclusions(self):
        out, _ = t.plan(PAYLOAD, "goalstats-user-service", "User")
        for p in [
            t.MIGRATION,
            "requirements.txt",
            "Makefile",
            "mypy.ini",
            "pytest.ini",
            "ruff.toml",
            *[p for p in PAYLOAD if p.startswith("make/")],
        ]:
            self.assertEqual(out[p], PAYLOAD[p])
        d = b"Item Action ItemStatus ActionType /items /actions goalstats_database goalstats_test_runtime template GoalStats User"
        self.assertEqual(
            t.transform(d, t.identity("goalstats-user-service", "User"), "notes.md"), d
        )

    def test_embedded_and_residual(self):
        for token in [
            b"xgoalstats_template",
            b"goalstats_templateExtra",
            b"x-goalstats-template-py",
            b"goalstats-template-pyExtra",
            b"goalstats-template-other",
            b"GoalStats.Template",
            b"TemplateDbContext",
        ]:
            with self.subTest(token=token), self.assertRaises(ValueError):
                t.transform(
                    token, t.identity("goalstats-user-service", "User"), "notes.md"
                )

    def test_ci_scoped(self):
        with self.assertRaises(ValueError):
            t.transform(
                b"goalstats-template-${{",
                t.identity("goalstats-user-service", "User"),
                "notes.md",
            )

    def test_bytes_modes_and_opaque(self):
        data = {
            **PAYLOAD,
            "example.py": ("100755", b"\xef\xbb\xbfItem Action\r\n"),
            "opaque.bin": ("100644", b"\x00\xffItem"),
        }
        out, _ = t.plan(data, "goalstats-user-service", "User")
        self.assertEqual(out["example.py"], ("100755", b"\xef\xbb\xbfItem Action\r\n"))
        self.assertEqual(out["opaque.bin"], data["opaque.bin"])

    def test_encoding_and_opaque_refusal(self):
        for path, d in [
            ("bad.py", b"\xff"),
            ("bad.py", b"\0"),
            ("opaque.bin", b"goalstats_template"),
        ]:
            with self.subTest(path=path, d=d), self.assertRaises(ValueError):
                t.plan(
                    {**PAYLOAD, path: ("100644", d)}, "goalstats-user-service", "User"
                )

    def test_collisions(self):
        for paths in [["a", "A"], ["a", "a/b"], ["Dir/a", "dir/b"]]:
            with self.assertRaises(ValueError):
                t.collision_check(paths)
        with self.assertRaises(ValueError):
            t.plan(
                {**PAYLOAD, "src/goalstats_user/main.py": ("100644", b"x")},
                "goalstats-user-service",
                "User",
            )

    def test_paths_and_artifacts(self):
        for p in [
            "../a",
            "/a",
            "a//b",
            "a/./b",
            "a/.git/x",
            "a/CON.py",
            "bad name",
            "a.",
            "bin/a",
            "obj/a",
            "__pycache__/x",
            "venv/x",
            ".env.local",
            ".coverage",
            "pyproject.toml",
            "requirements-dev.txt",
            "old.csproj",
        ]:
            with self.subTest(path=p), self.assertRaises(ValueError):
                t.validate_path(p)

    def test_unsupported_mode(self):
        with self.assertRaises(ValueError):
            t.plan(
                {**PAYLOAD, "link": ("120000", b"a")}, "goalstats-user-service", "User"
            )

    def test_no_extra_path_renames(self):
        _, mapping = t.plan(PAYLOAD, "goalstats-user-service", "User")
        for a, b in mapping.items():
            self.assertEqual(a, b)

    def test_identity_locations_and_boundaries(self):
        values = t.identity("goalstats-user-service", "User")
        for token in t.TOKENS:
            with self.subTest(token=token), self.assertRaises(ValueError):
                t.transform(token, values, "unexpected.md")
        for path, token in [
            ("src/main.py", b"xgoalstats_template"),
            ("src/main.py", b"goalstats_templateExtra"),
            ("scripts/workflow.py", b"x-goalstats-template-py"),
            ("scripts/workflow.py", b"goalstats-template-pyExtra"),
            ("docker/compose.local.yml", b"goalstats_template_py_staging"),
        ]:
            with self.subTest(path=path, token=token), self.assertRaises(ValueError):
                t.transform(token, values, path)
        self.assertEqual(
            t.transform(b"\xef\xbb\xbfgoalstats_template\r\n", values, "src/main.py"),
            b"\xef\xbb\xbfgoalstats_user\r\n",
        )

    def test_flat_paths_and_imports_required(self):
        for path in [
            "src/goalstats_template/main.py",
            "src/goalstats_user/main.py",
            "src/__init__.py",
        ]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                t.plan(
                    {**PAYLOAD, path: ("100644", b"legacy")},
                    "goalstats-user-service",
                    "User",
                )
        for prefix in [b"goalstats_template", b"goalstats_user"]:
            data = dict(PAYLOAD)
            mode, original = data["src/main.py"]
            data["src/main.py"] = (
                mode,
                original + b"\nfrom " + prefix + b".models import Item\n",
            )
            with self.assertRaises(ValueError):
                t.plan(data, "goalstats-user-service", "User")
        output, mapping = t.plan(PAYLOAD, "goalstats-user-service", "User")
        self.assertEqual(set(output), set(PAYLOAD))
        self.assertEqual(mapping, {p: p for p in PAYLOAD})
        for path in PAYLOAD:
            if path.startswith("src/") and path not in {
                "src/main.py",
                "src/settings/base.py",
            }:
                self.assertEqual(output[path], PAYLOAD[path])
