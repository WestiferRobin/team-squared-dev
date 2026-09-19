"""Parent port bootstrap uses code defaults and preserves legacy overrides."""
import subprocess
import tempfile
import unittest
from pathlib import Path

HELPER = Path(__file__).resolve().parents[1] / 'scripts/infra-config.sh'

class InfraConfig(unittest.TestCase):
    def setup_in(self, root):
        return subprocess.run(['bash', '-c', 'source "$1"; infra_setup', 'bash', str(HELPER)], cwd=root, text=True, capture_output=True)

    def test_fresh_private_and_idempotent_without_examples(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(self.setup_in(root).returncode, 0)
            path = root / 'infra/.env.local'
            before = path.read_bytes()
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(self.setup_in(root).returncode, 0)
            self.assertEqual(path.read_bytes(), before)
            self.assertFalse((root / 'infra/.env.dev').exists())
            self.assertIn(b'LOCAL_FRONTEND_PORT=33000', before)
            self.assertIn(b'DEV_FRONTEND_PORT=33001', before)

    def test_migration_preserves_both_ports_and_backups(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'infra').mkdir()
            for mode, port in [('local', '33441'), ('dev', '33442')]:
                (root / ('infra/.env.' + mode)).write_text('FRONTEND_PORT=' + port + '\n')
            result = self.setup_in(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((root / 'infra/.env.local').read_text(), 'LOCAL_FRONTEND_PORT=33441\nDEV_FRONTEND_PORT=33442\n')
            self.assertFalse((root / 'infra/.env.dev').exists())
            self.assertEqual(len(list((root / 'infra/.config-state').glob('backup.*'))), 2)

    def test_conflicting_values_refused_without_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'infra').mkdir()
            path = root / 'infra/.env.local'
            content = 'FRONTEND_PORT=33010\nLOCAL_FRONTEND_PORT=33011\n'
            path.write_text(content)
            self.assertNotEqual(self.setup_in(root).returncode, 0)
            self.assertEqual(path.read_text(), content)
