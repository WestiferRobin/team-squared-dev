import unittest
from scaffold_fixtures import Fixture, load


class ServiceContract(Fixture, unittest.TestCase):
    def classify(self, incomplete=False):
        c = load("service-contract")
        c.s.ROOT = self.parent
        return c.classify(
            self.dest, "goalstats-user-service", "User", self.placeholder, incomplete
        )[0]

    def test_placeholder(self):
        self.assertEqual(self.classify(), "PLACEHOLDER")

    def test_dirty_placeholder(self):
        (self.dest / "README.md").write_text("old scaffold")
        self.assertEqual(self.classify(), "INVALID")

    def test_incomplete(self):
        self.assertEqual(self.classify(True), "INCOMPLETE")

    def test_scaffolded(self):
        p = self.invoke()
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertEqual(self.classify(), "SCAFFOLDED")

    def test_missing_anchor(self):
        self.assertEqual(self.invoke().returncode, 0)
        (self.dest / "Dockerfile").unlink()
        self.assertEqual(self.classify(), "INVALID")

    def test_mixed_legacy(self):
        self.assertEqual(self.invoke().returncode, 0)
        (self.dest / "src/old.cs").write_text("legacy")
        self.assertEqual(self.classify(), "INVALID")

    def test_guard_prevents_test_delegation(self):
        p = self.cmd(
            self.parent, "bash", "scripts/box.sh", "test", "local", "", ok=False
        )
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("PLACEHOLDER", p.stdout)
        self.assertIn("no active suite", p.stdout)

    def test_guard_prevents_runtime_tools(self):
        for action in ["build", "run", "migrate", "smoke"]:
            p = self.cmd(
                self.parent, "bash", "scripts/box.sh", action, "local", "", ok=False
            )
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("PLACEHOLDER", p.stdout)
            self.assertIn("no runtime tooling", p.stdout)
