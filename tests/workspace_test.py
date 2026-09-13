"""Real local Git fixtures. Run: python3 -m unittest discover -s tests -p '*_test.py'."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]

class Workspace(unittest.TestCase):
    def run_cmd(self, cwd, *args, ok=True):
        p = subprocess.run(args, cwd=cwd, env=self.env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if ok and p.returncode:
            self.fail(f'{args}: {p.stdout}')
        return p

    def git(self, cwd, *args):
        return self.run_cmd(cwd, 'git', *args).stdout.strip()

    def commit(self, repo, message='fixture'):
        self.git(repo, 'add', '.')
        self.git(repo, 'commit', '-qm', message)
        return self.git(repo, 'rev-parse', 'HEAD')

    def init(self, name):
        repo = self.base / name
        repo.mkdir()
        self.git(repo, 'init', '-q', '-b', 'master')
        (repo / 'content').write_text('initial\n')
        self.commit(repo)
        return repo

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='workspace-test-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.env = dict(os.environ, PATH='/usr/bin:/bin:/usr/sbin:/sbin', GIT_CONFIG_GLOBAL='/dev/null',
                        GIT_CONFIG_NOSYSTEM='1', GIT_ALLOW_PROTOCOL='file',
                        GIT_AUTHOR_NAME='Fixture', GIT_AUTHOR_EMAIL='fixture@example.invalid',
                        GIT_COMMITTER_NAME='Fixture', GIT_COMMITTER_EMAIL='fixture@example.invalid')
        self.assertIsNone(shutil.which('docker', path=self.env['PATH']))
        self.child = self.init('child')
        self.pin = self.git(self.child, 'rev-parse', 'HEAD')
        self.parent = self.init('parent')
        for name in ['Makefile', 'scripts/workspace.sh', 'scripts/git-safety.sh', 'scripts/box.sh', 'config/components.tsv',
                     'infra/.env.local.example', 'infra/.env.dev.example', '.gitignore']:
            dest = self.parent / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / name, dest)
        self.git(self.parent, 'submodule', 'add', '-q', str(self.child), 'children/one')
        self.commit(self.parent)
        self.work = self.base / 'work'
        self.git(self.base, 'clone', '-q', str(self.parent), str(self.work))
        self.before = self.git(self.work, 'rev-parse', 'HEAD')

    def make(self, action, ok=True):
        return self.run_cmd(self.work, 'make', action, ok=ok)

    def refuse(self, action, text):
        before = self.git(self.work, 'rev-parse', 'HEAD')
        p = self.make(action, ok=False)
        self.assertNotEqual(p.returncode, 0, p.stdout)
        self.assertIn(text, p.stdout)
        self.assertEqual(before, self.git(self.work, 'rev-parse', 'HEAD'))

    def advance(self):
        (self.child / 'content').write_text('approved\n')
        approved = self.commit(self.child)
        self.git(self.parent / 'children/one', 'fetch', 'origin')
        self.git(self.parent / 'children/one', 'checkout', '--detach', approved)
        self.commit(self.parent, 'approve child')
        (self.child / 'content').write_text('newer unapproved\n')
        self.commit(self.child)
        return approved

    def test_setup_fresh_repeat_branch_env_and_no_docker(self):
        self.git(self.work, 'switch', '-c', 'feature')
        p = self.make('setup')
        self.assertIn('runtime-pending', p.stdout)
        self.assertEqual(self.pin, self.git(self.work / 'children/one', 'rev-parse', 'HEAD'))
        self.git(self.work / 'children/one', 'switch', '-c', 'child-feature')
        envfile = self.work / 'infra/.env.local'
        envfile.write_bytes(b'private\x00bytes\n')
        self.make('setup')
        self.assertEqual(envfile.read_bytes(), b'private\x00bytes\n')
        self.assertEqual(self.before, self.git(self.work, 'rev-parse', 'HEAD'))
        self.assertEqual('child-feature', self.git(self.work / 'children/one', 'branch', '--show-current'))
        self.git(self.work, 'checkout', '--detach')
        self.make('setup')

    def test_sync_current_no_env(self):
        self.make('sync')
        self.assertFalse((self.work / 'infra/.env.local').exists())
        self.assertEqual(self.pin, self.git(self.work / 'children/one', 'rev-parse', 'HEAD'))

    def test_sync_ff_exact_pin_url_no_env_mutation(self):
        self.make('setup')
        envfile = self.work / 'infra/.env.local'
        envfile.write_bytes(b'keep\n')
        approved = self.advance()
        self.git(self.work, 'config', 'submodule.children/one.url', '/invalid')
        self.git(self.work / 'children/one', 'remote', 'set-url', 'origin', '/invalid')
        self.git(self.work, 'config', 'submodule.recurse', 'true')
        self.git(self.work, 'config', 'fetch.recurseSubmodules', 'true')
        self.make('sync')
        self.assertEqual(approved, self.git(self.work / 'children/one', 'rev-parse', 'HEAD'))
        self.assertEqual(str(self.child), self.git(self.work / 'children/one', 'remote', 'get-url', 'origin'))
        self.assertEqual(envfile.read_bytes(), b'keep\n')
        self.assertEqual(self.git(self.parent, 'rev-parse', 'HEAD'), self.git(self.work, 'rev-parse', 'HEAD'))

    def test_parent_safety(self):
        for kind in ['untracked', 'tracked', 'staged', 'metadata', 'staged-metadata']:
            with self.subTest(kind=kind):
                path = self.work / ('TODO.md' if kind == 'untracked' else '.gitmodules' if 'metadata' in kind else 'content')
                original = path.read_bytes() if path.exists() else None
                path.write_text('unsafe\n')
                if kind.startswith('staged'):
                    self.git(self.work, 'add', str(path))
                for action in ['setup', 'sync']:
                    self.refuse(action, 'Unsafe work preserved')
                self.assertFalse((self.work / 'infra/.env.local').exists())
                self.git(self.work, 'reset', '-q', 'HEAD', '--', str(path))
                if original is None: path.unlink()
                else: path.write_bytes(original)

    def test_child_dirty_and_offpin(self):
        self.make('setup')
        self.advance()
        child = self.work / 'children/one'
        for kind in ['untracked', 'tracked', 'staged']:
            path = child / ('extra' if kind == 'untracked' else 'content')
            path.write_text('work\n')
            if kind == 'staged': self.git(child, 'add', '.')
            for action in ['setup', 'sync']: self.refuse(action, 'Unsafe work preserved')
            self.git(child, 'reset', '--hard', 'HEAD')
            if kind == 'untracked': path.unlink()
        (child / 'content').write_text('unpublished\n')
        self.commit(child)
        for action in ['setup', 'sync']: self.refuse(action, 'off-pin child preserved')

    def test_staged_gitlink(self):
        self.make('setup')
        child = self.work / 'children/one'
        (child / 'content').write_text('work\n')
        self.commit(child)
        self.git(self.work, 'add', 'children/one')
        for action in ['setup', 'sync']: self.refuse(action, 'Unsafe work preserved')

    def test_occupied_path(self):
        path = self.work / 'children/one/private'
        path.write_text('preserve')
        for action in ['setup', 'sync']: self.refuse(action, 'nonempty child path')
        self.assertEqual('preserve', path.read_text())

    def test_parent_branch_ahead_divergent(self):
        self.git(self.work, 'switch', '-c', 'feature')
        self.refuse('sync', 'requires parent master')
        self.git(self.work, 'checkout', '--detach')
        self.refuse('sync', 'requires parent master')
        self.git(self.work, 'switch', 'master')
        (self.work / 'content').write_text('local\n')
        self.commit(self.work)
        self.refuse('sync', 'locally ahead or divergent')
        (self.parent / 'content').write_text('remote\n')
        self.commit(self.parent)
        self.refuse('sync', 'locally ahead or divergent')

    def test_operation_markers_parent_child(self):
        self.make('setup')
        for repo in [self.work, self.work / 'children/one']:
            for marker in ['MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply', 'sequencer']:
                path = Path(self.git(repo, 'rev-parse', '--absolute-git-dir')) / marker
                if marker in ['rebase-merge', 'rebase-apply', 'sequencer']: path.mkdir()
                else: path.write_text(self.pin + '\n')
                for action in ['setup', 'sync']: self.refuse(action, 'operation in progress')
                if path.is_dir(): path.rmdir()
                else: path.unlink()

    def test_incoming_removal(self):
        self.make('setup')
        self.git(self.parent, 'rm', '-f', 'children/one')
        self.commit(self.parent)
        self.refuse('sync', 'removal/rename')

    def test_ignored_collision(self):
        (self.work / 'artifacts').mkdir()
        (self.work / 'artifacts/keep').write_text('local')
        self.make('setup')
        (self.parent / 'artifacts').mkdir()
        (self.parent / 'artifacts/keep').write_text('incoming')
        self.git(self.parent, 'add', '-f', 'artifacts/keep')
        self.commit(self.parent)
        self.refuse('sync', 'replace ignored file')
        self.assertEqual('local', (self.work / 'artifacts/keep').read_text())

    def test_partial_download_retry(self):
        self.make('setup')
        approved = self.advance()
        unavailable = self.base / 'unavailable'
        self.git(self.parent, 'config', '-f', '.gitmodules', 'submodule.children/one.url', str(unavailable))
        self.commit(self.parent)
        p = self.make('sync', ok=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('retry: make sync', p.stdout)
        self.assertEqual(self.git(self.parent, 'rev-parse', 'HEAD'), self.git(self.work, 'rev-parse', 'HEAD'))
        self.assertEqual(self.pin, self.git(self.work / 'children/one', 'rev-parse', 'HEAD'))
        self.git(self.base, 'clone', '--bare', str(self.child), str(unavailable))
        self.make('sync')
        self.assertEqual(approved, self.git(self.work / 'children/one', 'rev-parse', 'HEAD'))

    def test_nested_dirty_offpin(self):
        nested = self.init('nested')
        self.git(self.child, 'submodule', 'add', '-q', str(nested), 'nested')
        sha = self.commit(self.child)
        self.git(self.parent / 'children/one', 'fetch', 'origin')
        self.git(self.parent / 'children/one', 'checkout', '--detach', sha)
        self.commit(self.parent)
        self.make('sync')
        path = self.work / 'children/one/nested'
        (path / 'content').write_text('nested work')
        for action in ['setup', 'sync']: self.refuse(action, 'Unsafe work preserved')
        self.commit(path)
        for action in ['setup', 'sync']: self.refuse(action, 'off-pin child preserved')

    def test_setup_does_not_fetch_parent(self):
        self.advance()
        self.git(self.work, 'remote', 'set-url', 'origin', '/unavailable-parent')
        self.make('setup')
        self.assertEqual(self.before, self.git(self.work, 'rev-parse', 'HEAD'))
        self.assertEqual(self.pin, self.git(self.work / 'children/one', 'rev-parse', 'HEAD'))

    def test_new_child_and_updated_helper(self):
        self.make('setup')
        extra = self.init('extra')
        self.git(self.parent, 'submodule', 'add', '-q', str(extra), 'children/two')
        helper = self.parent / 'scripts/workspace.sh'
        helper.write_text(helper.read_text().replace('Workspace ready.', 'Updated helper loaded. Workspace ready.'))
        self.commit(self.parent)
        p = self.make('sync')
        self.assertIn('Updated helper loaded.', p.stdout)
        self.assertEqual(self.git(extra, 'rev-parse', 'HEAD'), self.git(self.work / 'children/two', 'rev-parse', 'HEAD'))

    def test_real_merge_conflict(self):
        self.git(self.work, 'switch', '-c', 'conflict')
        (self.work / 'content').write_text('side one\n')
        self.commit(self.work)
        self.git(self.work, 'switch', 'master')
        (self.work / 'content').write_text('side two\n')
        self.commit(self.work)
        p = self.run_cmd(self.work, 'git', 'merge', 'conflict', ok=False)
        self.assertNotEqual(p.returncode, 0)
        for action in ['setup', 'sync']: self.refuse(action, 'operation in progress')
        self.assertIn('<<<<<<<', (self.work / 'content').read_text())

    def test_ignored_directory_replaced_by_file(self):
        self.make('setup')
        (self.work / 'artifacts').mkdir()
        (self.work / 'artifacts/private').write_text('keep')
        (self.parent / 'artifacts').write_text('replace directory')
        self.git(self.parent, 'add', '-f', 'artifacts')
        self.commit(self.parent)
        self.refuse('sync', 'replace ignored file')
        self.assertEqual('keep', (self.work / 'artifacts/private').read_text())

    def test_nested_operation_and_staged_gitlink(self):
        nested = self.init('nested')
        self.git(self.child, 'submodule', 'add', '-q', str(nested), 'nested')
        sha = self.commit(self.child)
        self.git(self.parent / 'children/one', 'fetch', 'origin')
        self.git(self.parent / 'children/one', 'checkout', '--detach', sha)
        self.commit(self.parent)
        self.make('sync')
        path = self.work / 'children/one/nested'
        marker = Path(self.git(path, 'rev-parse', '--absolute-git-dir')) / 'CHERRY_PICK_HEAD'
        marker.write_text(self.git(path, 'rev-parse', 'HEAD') + '\n')
        for action in ['setup', 'sync']: self.refuse(action, 'operation in progress')
        marker.unlink()
        (path / 'content').write_text('nested work')
        self.commit(path)
        self.git(path.parent, 'add', 'nested')
        for action in ['setup', 'sync']: self.refuse(action, 'Unsafe work preserved')

    def test_partial_retry_rejects_unrelated_commit(self):
        self.make('setup')
        self.advance()
        self.git(self.parent, 'config', '-f', '.gitmodules', 'submodule.children/one.url', '/unavailable')
        self.commit(self.parent)
        self.assertNotEqual(self.make('sync', ok=False).returncode, 0)
        child = self.work / 'children/one'
        (child / 'content').write_text('unrelated unpublished work')
        self.commit(child)
        self.refuse('sync', 'off-pin child preserved')

if __name__ == '__main__':
    unittest.main()
