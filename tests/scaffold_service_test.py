"""Scaffold fixtures use real Git; never scaffold the developer's child repositories."""
import hashlib
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import time
import unittest

SOURCE = Path(__file__).resolve().parents[1]
SERVICE = 'goalstats-user-service'
SOURCE_PATH = 'backend/template-goalstats-service'
DEST_PATH = 'backend/' + SERVICE

class Scaffold(unittest.TestCase):
    def cmd(self, repo, *args, ok=True, env=None):
        p = subprocess.run(args, cwd=repo, env=env or self.env, text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if ok and p.returncode:
            self.fail(f'{args}\n{p.stdout}')
        return p

    def git(self, repo, *args):
        return self.cmd(repo, 'git', *args).stdout.strip()

    def commit(self, repo):
        self.git(repo, 'add', '-A')
        self.git(repo, 'commit', '-qm', 'fixture')
        return self.git(repo, 'rev-parse', 'HEAD')

    def init(self, name):
        path = self.base / name
        path.mkdir()
        self.git(path, 'init', '-q', '-b', 'master')
        return path

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='scaffold-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.env = dict(os.environ, PATH='/usr/bin:/bin:/usr/sbin:/sbin',
                        TMPDIR=str(self.base), GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1',
                        GIT_ALLOW_PROTOCOL='file', GIT_OPTIONAL_LOCKS='0',
                        GIT_AUTHOR_NAME='Fixture', GIT_AUTHOR_EMAIL='fixture@example.invalid',
                        GIT_COMMITTER_NAME='Fixture', GIT_COMMITTER_EMAIL='fixture@example.invalid')
        for key in ['SERVICE', 'DOMAIN', 'DRY_RUN', 'MAKEFLAGS', 'MFLAGS', 'MAKEOVERRIDES']:
            self.env.pop(key, None)
        self.assertIsNone(shutil.which('docker', path=self.env['PATH']))
        source = self.init('template-remote')
        (source / 'README.md').write_text('# Template\n')
        (source / '.gitignore').write_text('.env\n.env.*\n!.env.example\nbin/\n')
        (source / '.env.example').write_text('EXAMPLE=disposable\n')
        (source / 'scripts').mkdir()
        for name in ['smoke.sh', 'test.sh']:
            f = source / 'scripts' / name
            f.write_text('#!/bin/sh\nexit 0\n')
            f.chmod(0o755)
        (source / 'scripts/develop.sh').write_text('echo tooling\n')
        (source / 'src').mkdir()
        (source / 'src/Service.cs').write_text('// template source\n')
        # Hand-authored identity fixture and golden output, independent of production code.
        self.identity_files = {}
        for identity in ['Template', 'User']:
            api = 'src/GoalStats.' + identity + '.Api'
            ctx = identity + 'DbContext'
            self.identity_files[identity] = {
                'GoalStats.'+identity+'.sln': 'GoalStats.'+identity+'.Api\n',
                api+'/GoalStats.'+identity+'.Api.csproj': '<Project />\n',
                api+'/Infrastructure/Database/'+ctx+'.cs': 'class '+ctx+' {}\n',
                api+'/Infrastructure/Database/Migrations/'+ctx+'ModelSnapshot.cs': 'class '+ctx+'ModelSnapshot {}\n',
                'tests/GoalStats.'+identity+'.Api.UnitTests/GoalStats.'+identity+'.Api.UnitTests.csproj': 'GoalStats.'+identity+'.Api\n',
                'tests/GoalStats.'+identity+'.Api.IntegrationTests/GoalStats.'+identity+'.Api.IntegrationTests.csproj': 'GoalStats.'+identity+'.Api\n',
                'tests/GoalStats.'+identity+'.Api.IntegrationTests/Infrastructure/Database/'+ctx+'Tests.cs': 'class '+ctx+'Tests {}\n',
                'identity.md': 'goalstats-'+identity.lower()+'-api goalstats_'+identity.lower()+'_local\n',
            }
        for name, content in self.identity_files['Template'].items():
            file=source/name; file.parent.mkdir(parents=True,exist_ok=True); file.write_text(content)
        self.source_pin = self.commit(source)
        target = self.init('destination-remote')
        (target / 'README.md').write_text('# ' + SERVICE + '\n')
        (target / '.gitignore').write_text('.env\nbin/\n')
        self.placeholder = self.commit(target)
        self.parent = self.init('parent')
        for name in ['Makefile','scripts/workspace.sh','scripts/git-safety.sh','scripts/box.sh',
                     'scripts/scaffold-service.sh','scripts/scaffold-transform.py','.gitignore','infra/.env.local.example','infra/.env.dev.example']:
            dest = self.parent / name
            dest.parent.mkdir(exist_ok=True, parents=True)
            shutil.copyfile(SOURCE / name, dest)
        (self.parent / 'config').mkdir()
        (self.parent / 'config/components.tsv').write_text(
            'reference\tservice-template\t'+SOURCE_PATH+'\tnone\tnone\tnone\tnone\tnone\tnone\n'
            'active\tuser-service\t'+DEST_PATH+'\tnone\tnone\tnone\tnone\tnone\tnone\n')
        self.approvals = self.parent / 'config/scaffolds.tsv'
        self.approvals.write_text('# service\tplaceholder-commit\n'+SERVICE+'\t'+self.placeholder+'\tUser\n')
        for remote, path in [(source, SOURCE_PATH), (target, DEST_PATH)]:
            self.git(self.parent, 'submodule', 'add', '-q', str(remote), path)
        self.commit(self.parent)
        self.src = self.parent / SOURCE_PATH
        self.dest = self.parent / DEST_PATH
        # Default fixture is already on master; detached workflows are explicit below.

    def identity(self, repo):
        gitdir = Path(self.git(repo, 'rev-parse', '--absolute-git-dir'))
        return (self.git(repo, 'rev-parse', 'HEAD'),
                self.git(repo, 'branch', '--show-current'), self.git(repo, 'show-ref'),
                self.git(repo, 'rev-list', '--all'), self.git(repo, 'config', '--local', '--list'),
                (gitdir / 'index').read_bytes(),
                (repo / '.git').read_bytes() if (repo / '.git').is_file() else str(gitdir))

    def tree(self, repo):
        out = {}
        for path in repo.rglob('*'):
            rel = path.relative_to(repo)
            if '.git' in rel.parts:
                continue
            if path.is_symlink(): out[str(rel)] = ('symlink', os.readlink(path))
            elif path.is_file(): out[str(rel)] = (path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
        return out

    def invoke(self, dry=None, service=SERVICE, direct=False, env=None, domain="User"):
        if direct:
            e = dict(env or self.env, SERVICE=service, DOMAIN=domain)
            if dry is not None: e['DRY_RUN'] = dry
            return self.cmd(self.parent, '/bin/bash', 'scripts/scaffold-service.sh', ok=False, env=e)
        args = ['make', 'scaffold-service', 'SERVICE='+service, 'DOMAIN='+domain]
        if dry is not None: args.append('DRY_RUN='+dry)
        return self.cmd(self.parent, *args, ok=False, env=env)

    def refuse(self, text=None, **kwargs):
        before = self.tree(self.dest)
        # Detached HEAD is a valid test input; capture Git files without requiring symbolic-ref.
        index = Path(self.git(self.dest, 'rev-parse', '--absolute-git-dir')) / 'index'
        git_before = (self.git(self.dest,'rev-parse','HEAD'), index.read_bytes(), (self.dest/'.git').read_bytes())
        p = self.invoke(**kwargs)
        self.assertNotEqual(p.returncode, 0, p.stdout)
        if text: self.assertIn(text, p.stdout)
        self.assertEqual(before, self.tree(self.dest))
        self.assertEqual(git_before, (self.git(self.dest,'rev-parse','HEAD'), index.read_bytes(), (self.dest/'.git').read_bytes()))
        return p

    def approve_source(self):
        self.source_pin = self.commit(self.src)
        self.commit(self.parent)

    def approve_destination(self):
        self.placeholder = self.commit(self.dest)
        self.git(self.dest, 'update-ref', 'refs/remotes/origin/master', self.placeholder)
        self.approvals.write_text(SERVICE+'\t'+self.placeholder+'\tUser\n')
        self.commit(self.parent)

    def test_success_exact_payload_and_identity(self):
        before = self.identity(self.dest), self.identity(self.parent)
        p = self.invoke(dry='false')
        self.assertEqual(0, p.returncode, p.stdout)
        expected=self.tree(self.src)
        for name in self.identity_files['Template']: del expected[name]
        expected.update({name:(content.encode(),0o644) for name,content in self.identity_files['User'].items()})
        self.assertEqual(expected, self.tree(self.dest))
        self.assertEqual(before, (self.identity(self.dest), self.identity(self.parent)))
        self.assertIn('Scaffold complete', p.stdout)
        self.assertFalse((self.parent/'.git/team-squared-scaffold-incomplete').exists())
        self.assertEqual([], list(self.base.glob('team-squared-scaffold*')))

    def test_dry_run(self):
        before = self.tree(self.dest), self.identity(self.dest), self.identity(self.parent)
        p = self.invoke(dry='true')
        self.assertEqual(0, p.returncode, p.stdout)
        self.assertIn('REPLACE approved placeholder README.md',p.stdout)
        self.assertIn('ADD src/Service.cs',p.stdout)
        self.assertEqual(before,(self.tree(self.dest),self.identity(self.dest),self.identity(self.parent)))
        self.assertEqual([], list(self.base.glob('team-squared-scaffold*')))

    def repository_snapshot(self):
        return {str(p.relative_to(self.parent)): p.read_bytes()
                for p in self.parent.rglob('*') if p.is_file()}

    def test_fresh_detached_preview_then_install(self):
        self.git(self.dest, 'checkout', '--detach', self.placeholder)
        before = self.repository_snapshot()
        identity = self.identity(self.dest)
        preview = self.invoke(dry='true')
        self.assertEqual(0, preview.returncode, preview.stdout)
        self.assertIn('PLANNED BRANCH ACTION: ATTACH TO master', preview.stdout)
        self.assertEqual(before, self.repository_snapshot())
        result = self.invoke(dry='false')
        self.assertEqual(0, result.returncode, result.stdout)
        after = self.identity(self.dest)
        self.assertEqual('master', after[1])
        self.assertEqual(identity[:1] + identity[2:], after[:1] + after[2:])
        self.assertIn(self.placeholder, self.git(self.parent, 'ls-tree', 'HEAD', DEST_PATH))
        for dry in ['true', 'false']: self.refuse(dry=dry)
        self.commit(self.dest)
        for dry in ['true', 'false']: self.refuse(dry=dry)

    def test_missing_and_mismatched_master_refs(self):
        self.git(self.dest, 'checkout', '--detach')
        for ref in ['refs/heads/master', 'refs/remotes/origin/master']:
            self.git(self.dest, 'update-ref', '-d', ref)
            self.refuse('is missing', dry='true')
            self.git(self.dest, 'update-ref', ref, self.placeholder)
        (self.dest/'README.md').write_text('new')
        newer = self.commit(self.dest)
        self.git(self.dest, 'checkout', '--detach', self.placeholder)
        for ref in ['refs/heads/master', 'refs/remotes/origin/master']:
            self.git(self.dest, 'update-ref', ref, newer)
            self.refuse('must match', dry='false')
            self.git(self.dest, 'update-ref', ref, self.placeholder)

    def test_master_owned_by_linked_worktree(self):
        self.git(self.dest, 'checkout', '--detach')
        self.git(self.dest, 'worktree', 'add', str(self.base/'linked'), 'master')
        for dry in ['true', 'false']: self.refuse('another worktree', dry=dry)

    def test_attachment_failure(self):
        self.git(self.dest, 'checkout', '--detach')
        env=self.wrapper('git', 'for arg in "$@"; do if [[ "$arg" == "scaffold: attach approved destination to master" ]]; then exit 17; fi; done\nexec /usr/bin/git "$@"\n')
        self.refuse('could not attach', dry='false', env=env)
        self.assertEqual('', self.git(self.dest, 'branch', '--show-current'))

    def test_attachment_preserves_placeholder_before_copy(self):
        self.git(self.dest, 'checkout', '--detach')
        before=self.tree(self.dest), self.identity(self.dest)
        env=self.wrapper('cp', 'case "$1" in */backend/goalstats-user-service/README.md) exit 17 ;; esac\nexec /bin/cp "$@"\n')
        result=self.invoke(dry='false', env=env)
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(before[0], self.tree(self.dest))
        after=self.identity(self.dest)
        self.assertEqual('master', after[1])
        self.assertEqual(before[1][:1]+before[1][2:], after[:1]+after[2:])

    def test_post_attachment_ref_change_refused(self):
        self.git(self.dest, 'checkout', '--detach')
        env=self.wrapper('git', '/usr/bin/git "$@" || exit $?\nfor arg in "$@"; do if [[ "$arg" == "scaffold: attach approved destination to master" ]]; then /usr/bin/git -C "'+str(self.dest)+'" update-ref -d refs/remotes/origin/master; fi; done\n')
        self.refuse('is missing', dry='false', env=env)
        self.assertEqual('master', self.git(self.dest, 'branch', '--show-current'))

    def test_branch_change_during_preparation(self):
        self.git(self.dest, 'checkout', '--detach')
        env=self.wrapper('tar', '/usr/bin/tar "$@" || exit $?\n/usr/bin/git -C "'+str(self.dest)+'" symbolic-ref HEAD refs/heads/master\n')
        self.refuse('branch changed during preparation', dry='true', env=env)

    def test_ref_change_during_preparation(self):
        env=self.wrapper('tar', '/usr/bin/tar "$@" || exit $?\n/usr/bin/git -C "'+str(self.dest)+'" update-ref -d refs/remotes/origin/master\n')
        self.refuse('is missing', dry='false', env=env)

    def test_invalid_dry_run(self):
        for value in ['', 'yes', '1', 'TRUE', 'false;echo invalid']:
            with self.subTest(value=value): self.refuse('DRY_RUN accepts', dry=value)

    def test_input_security(self):
        for value in ['', '../user','/tmp/user','-service','goalstats-user-service;touch injected',
                      'goalstats-user-service\n','goalstats user-service','goalstats\\user-service',
                      '$(shell touch injected)', '`touch injected`', '$(touch injected)']:
            with self.subTest(value=value): self.refuse('SERVICE must', service=value)
        self.assertFalse((self.parent/'injected').exists())
        self.refuse('DRY_RUN accepts', dry='$(shell touch injected)')
        self.assertFalse((self.parent/'injected').exists())

    def test_unknown_targets(self):
        for value in ['goalstats-other-service','template-goalstats-service','goal-stats-app','goal-stats-wiki','RoadToTheFinal']:
            with self.subTest(value=value): self.refuse(service=value)

    def test_source_dirty_staged_untracked(self):
        path=self.src/'README.md'; original=path.read_bytes()
        path.write_text('customized')
        self.refuse('Unsafe work preserved')
        self.git(self.src,'add','README.md'); self.refuse('Unsafe work preserved')
        self.git(self.src,'reset','HEAD','README.md'); path.write_bytes(original)
        (self.src/'extra').write_text('untracked'); self.refuse('Unsafe work preserved')

    def test_source_ignored_files_not_exported(self):
        (self.src/'.env.local').write_text('not copied')
        p=self.invoke(); self.assertEqual(0,p.returncode,p.stdout)
        self.assertFalse((self.dest/'.env.local').exists())

    def test_source_offpin(self):
        (self.src/'README.md').write_text('newer unapproved')
        self.commit(self.src); self.refuse('off-pin')

    def test_newer_source_branch_ignored(self):
        self.git(self.src,'switch','-c','newer')
        (self.src/'README.md').write_text('newer unapproved')
        newer=self.commit(self.src)
        self.git(self.src,'update-ref','refs/remotes/origin/master',newer)
        self.git(self.src,'checkout','--detach',self.source_pin)
        p=self.invoke(); self.assertEqual(0,p.returncode,p.stdout)
        self.assertEqual('# Template\n',(self.dest/'README.md').read_text())

    def test_wrong_origins(self):
        for repo in [self.src,self.dest]:
            url=self.git(repo,'remote','get-url','origin')
            self.git(repo,'remote','set-url','origin','/wrong')
            self.refuse('noncanonical origin')
            self.git(repo,'remote','set-url','origin',url)

    def test_missing_source(self):
        self.git(self.parent,'submodule','deinit','-f',SOURCE_PATH)
        self.refuse('initialized')

    def test_destination_branches(self):
        for branch in ['main','feat/bootstrap','fix/bootstrap','feature/x','develop','dev','other']:
            self.git(self.dest,'switch','-C',branch)
            self.refuse('destination must be master')
        self.git(self.dest,'checkout','--detach')
        self.assertEqual(0, self.invoke(dry='true').returncode)

    def test_destination_dirty_staged_custom_readme(self):
        (self.dest/'README.md').write_text('valuable work')
        self.refuse('Unsafe work preserved')
        self.git(self.dest,'add','README.md')
        self.refuse('Unsafe work preserved')
        self.commit(self.dest)
        self.refuse('off-pin')

    def test_destination_untracked_and_ignored(self):
        for name in ['unexpected','.env','bin/private']:
            path=self.dest/name; path.parent.mkdir(exist_ok=True,parents=True)
            path.write_text('preserve')
            self.refuse()
            path.unlink()

    def test_wrong_placeholder(self):
        self.approvals.write_text(SERVICE+'\t'+'0'*40+'\tUser\n')
        self.commit(self.parent)
        self.refuse('Unresolved placeholder')

    def test_unexpected_approved_tracked_file(self):
        (self.dest/'extra').write_text('valuable')
        self.approve_destination()
        self.refuse('only regular README.md')

    def test_ignore_compatibility(self):
        for value in ['.env\nbin/\ncustom/\n','!important\n','.env.*\n']:
            (self.dest/'.gitignore').write_text(value)
            self.approve_destination()
            self.refuse()

    def test_registry_malformed(self):
        valid=SERVICE+'\t'+self.placeholder+'\tUser\n'
        for text in [valid+valid,SERVICE+' '+self.placeholder,valid.rstrip()+'\textra\n','../bad\t'+self.placeholder+'\tUser\n']:
            self.approvals.write_text(text);self.commit(self.parent);self.refuse()

    def test_missing_component_mapping(self):
        (self.parent/'config/components.tsv').write_text('')
        self.commit(self.parent); self.refuse('component mapping')

    def test_missing_submodule_mapping(self):
        self.git(self.parent,'config','-f','.gitmodules','--remove-section','submodule.'+DEST_PATH)
        self.commit(self.parent);self.refuse('Unregistered gitlink')

    def test_parent_dirty(self):
        path=self.parent/'README.md'
        path.write_text('parent');self.commit(self.parent)
        path.write_text('work');self.refuse('Unsafe work preserved')
        self.git(self.parent,'add','README.md');self.refuse('Unsafe work preserved')
        self.git(self.parent,'reset','HEAD','README.md');path.write_text('parent')
        (self.parent/'TODO.md').write_text('preserve');self.refuse('TODO.md')

    def test_parent_staged_gitlink(self):
        (self.src/'README.md').write_text('new');self.commit(self.src)
        self.git(self.parent,'add',SOURCE_PATH)
        self.refuse('Unsafe work preserved')

    def test_operations(self):
        for repo in [self.parent,self.src,self.dest]:
            gitdir=Path(self.git(repo,'rev-parse','--absolute-git-dir'))
            for marker in ['MERGE_HEAD','CHERRY_PICK_HEAD','REVERT_HEAD','rebase-merge','rebase-apply','sequencer','BISECT_START']:
                path=gitdir/marker;path.write_text(self.placeholder+'\tUser\n')
                self.refuse('operation in progress')
                path.unlink()

    def test_unrelated_child(self):
        other=self.init('unrelated');(other/'README.md').write_text('other');self.commit(other)
        self.git(self.parent,'submodule','add','-q',str(other),'frontend/other')
        self.commit(self.parent)
        child=self.parent/'frontend/other'
        self.git(child,'switch','-c','feat/unrelated')
        (child/'README.md').write_text('unpublished');self.commit(child)
        (child/'README.md').write_text('dirty')
        before=self.tree(child),self.identity(child)
        p=self.invoke();self.assertEqual(0,p.returncode,p.stdout)
        self.assertEqual(before,(self.tree(child),self.identity(child)))

    def test_forbidden_artifacts(self):
        for name in ['.env.local','bin/file','Obj/file','TestResults/file','artifacts/file','coverage/file','logs/file',
                     '.vs/file','.vscode/file','.idea/file','local.user','local.suo','.DS_Store','local.log',
                     'local.dump','local.backup','local.rdb','local.aof','local.sqlite','local.sqlite3',
                     'docker/data/file','docker/volumes/file','pgdata/file','postgres-data/file','redis-data/file']:
            path=self.src/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('runtime')
            self.git(self.src,'add','-f',name);self.git(self.src,'commit','-qm','forbidden')
            self.commit(self.parent);self.refuse('Forbidden')
            self.git(self.src,'rm',name);self.git(self.src,'commit','-qm','remove fixture artifact');self.commit(self.parent)

    def test_payload_symlink(self):
        (self.src/'link').symlink_to('/tmp')
        self.approve_source();self.refuse('Unsupported payload type')

    def test_nested_gitlink(self):
        self.git(self.src,'update-index','--add','--cacheinfo','160000,'+self.placeholder+',nested')
        self.git(self.src,'commit','-qm','nested');self.commit(self.parent)
        self.refuse('Unsupported payload type')

    def test_archive_export_ignore(self):
        (self.src/'.gitattributes').write_text('README.md export-ignore\n')
        self.approve_source();self.refuse('Payload missing')

    def test_archive_export_subst(self):
        (self.src/'.gitattributes').write_text('README.md export-subst\n')
        (self.src/'README.md').write_text('$Format:%H$\n')
        self.approve_source();self.refuse('Payload content mismatch')

    def test_local_export_attribute(self):
        gitdir=Path(self.git(self.src,'rev-parse','--absolute-git-dir'))
        (gitdir/'info/attributes').write_text('README.md export-ignore\n')
        self.refuse('Payload missing')

    def test_repeat_uncommitted_and_committed(self):
        p=self.invoke();self.assertEqual(0,p.returncode,p.stdout)
        self.refuse('Unsafe work preserved')
        self.commit(self.dest);self.refuse('off-pin')

    def test_independence(self):
        # No transport is permitted inside the helper, even local file transport.
        self.git(self.src,'config','remote.origin.promisor','true')
        p=self.invoke(env=dict(self.env,GIT_ALLOW_PROTOCOL=''))
        self.assertEqual(0,p.returncode,p.stdout)
        self.assertIsNone(shutil.which('docker',path=self.env['PATH']))

    def wrapper(self, name, body):
        directory=self.base/'wrappers';directory.mkdir(exist_ok=True)
        script=directory/name;script.write_text('#!/bin/bash\n'+body);script.chmod(0o755)
        return dict(self.env,PATH=str(directory)+':'+self.env['PATH'])

    def test_temp_failure(self):
        env=self.wrapper('mktemp','exit 17\n')
        p=self.refuse(direct=True,env=env)
        self.assertEqual(1,p.returncode)
        self.assertFalse((self.parent/'.git/team-squared-scaffold-incomplete').exists())

    def test_archive_failure(self):
        env=self.wrapper('tar','exit 17\n')
        p=self.refuse(direct=True,env=env)
        self.assertEqual(1,p.returncode)
        self.assertEqual([],list(self.base.glob('team-squared-scaffold*')))

    def test_mid_install_failure(self):
        env=self.wrapper('cp', 'case "$2" in */backend/goalstats-user-service/README.md) exit 17 ;; esac\nexec /bin/cp "$@"\n')
        before=self.identity(self.dest),self.identity(self.parent)
        p=self.invoke(direct=True,env=env)
        self.assertEqual(1,p.returncode,p.stdout)
        self.assertIn('INCOMPLETE at: README.md',p.stdout)
        self.assertEqual(before,(self.identity(self.dest),self.identity(self.parent)))
        journal=self.parent/'.git/team-squared-scaffold-incomplete'
        recovery=Path((journal/'recovery-directory').read_text().strip())
        self.assertTrue((recovery/'completed.txt').read_text())
        self.assertTrue((recovery/'original/README.md').exists())
        for name in ['source-manifest.tsv','mapping.tsv','transformed.tsv','policy.json','parent.identity','dest.identity','failed-phase.txt']:
            self.assertTrue((recovery/name).is_file(),name)
        self.assertIn(self.source_pin,(recovery/'policy.json').read_text())
        self.assertIn('User',(recovery/'policy.json').read_text())
        self.assertEqual('README.md\n',(recovery/'failed-phase.txt').read_text())
        self.refuse('Incomplete scaffold')

    def test_final_verification_failure(self):
        env=self.wrapper('cp', '"/bin/cp" "$@" || exit $?\ncase "$2" in */backend/goalstats-user-service/src/Service.cs) printf corrupt >> "$2" ;; esac\n')
        p=self.invoke(direct=True,env=env)
        self.assertEqual(1,p.returncode,p.stdout)
        self.assertIn('Payload content mismatch',p.stdout)
        self.assertTrue((self.parent/'.git/team-squared-scaffold-incomplete').exists())

    def test_existing_operation_indicators(self):
        for name in ['team-squared-workspace-sync','team-squared-scaffold-incomplete']:
            path=self.parent/'.git'/name;path.mkdir()
            self.refuse();path.rmdir()

    def test_empty_destination_directory_refused(self):
        (self.dest/'empty').mkdir()
        self.refuse('Unexpected destination directories')

    def test_archive_extra_entry(self):
        env=self.wrapper('tar','/usr/bin/tar "$@" || exit $?\nmkdir "$4/unexpected"\n')
        self.refuse('Payload paths differ',env=env)

    def test_archive_git_entry(self):
        env=self.wrapper('tar','/usr/bin/tar "$@" || exit $?\nprintf unexpected > "$4/.git"\n')
        self.refuse('Payload paths differ',env=env)

    def test_archive_executable_loss(self):
        env=self.wrapper('tar','/usr/bin/tar "$@" || exit $?\nchmod 644 "$4/scripts/test.sh"\n')
        self.refuse('Missing executable bit',env=env)

    def test_exclusive_lock(self):
        gitdir=self.git(self.parent,'rev-parse','--absolute-git-dir')
        key=subprocess.check_output(['git','hash-object','--stdin'],input=gitdir.encode(),env=self.env).decode().strip()
        lock=Path('/tmp')/('team-squared-scaffold-'+key+'.lock')
        lock.mkdir()
        self.addCleanup(lock.rmdir)
        self.refuse('Scaffold lock exists')
        self.assertTrue(lock.exists())

    def test_missing_destination(self):
        self.git(self.parent,'submodule','deinit','-f',DEST_PATH)
        p=self.invoke(direct=True)
        self.assertEqual(2,p.returncode,p.stdout)
        self.assertIn('uninitialized',p.stdout)
        self.assertEqual([],list(self.dest.iterdir()))

    def test_pin_differs_from_valid_placeholder(self):
        (self.dest/'README.md').write_text('different committed placeholder')
        self.commit(self.dest);self.commit(self.parent)
        self.refuse('differs from approved placeholder')

    def test_placeholder_mode_refused(self):
        (self.dest/'README.md').chmod(0o755)
        self.approve_destination()
        self.refuse('only regular README.md')

    def test_template_negation_refused(self):
        (self.src/'.gitignore').write_text('.env\nbin/\n!private\n')
        self.approve_source();self.refuse('Unsupported template ignore negation')

    def test_identical_ignore_with_negations(self):
        (self.src/'.gitignore').write_text('.env\nbin/\n!public\n')
        self.approve_source()
        (self.dest/'.gitignore').write_bytes((self.src/'.gitignore').read_bytes())
        self.approve_destination()
        p=self.invoke();self.assertEqual(0,p.returncode,p.stdout)

    def test_network_commands_never_attempted(self):
        self.git(self.dest, 'checkout', '--detach')
        log=self.base/'network-attempts'
        env=self.wrapper('git','for arg in "$@"; do\n case "$arg" in fetch|pull|ls-remote|clone) echo attempted >> "'+str(log)+'"; exit 88 ;; esac\ndone\nexec /usr/bin/git "$@"\n')
        for dry in ['true', 'false']:
            p=self.invoke(env=env, dry=dry)
            self.assertEqual(0,p.returncode,p.stdout)
        self.assertFalse(log.exists())

    def test_inactive_destination_refused(self):
        path=self.parent/'config/components.tsv'
        path.write_text(path.read_text().replace('active\tuser-service','reference\tuser-service'))
        self.commit(self.parent);self.refuse('Wrong component role')

    def test_destination_changes_during_export(self):
        env=self.wrapper('tar','/usr/bin/tar "$@" || exit $?\nmkdir "'+str(self.dest)+'/concurrent-directory"\n')
        p=self.invoke(env=env)
        self.assertNotEqual(0,p.returncode,p.stdout)
        self.assertIn('Unexpected destination directories',p.stdout)
        self.assertEqual('# '+SERVICE+'\n',(self.dest/'README.md').read_text())
        self.assertTrue((self.dest/'concurrent-directory').is_dir())
        self.assertFalse((self.parent/'.git/team-squared-scaffold-incomplete').exists())

    def test_directory_or_symlink_placeholder(self):
        path=self.dest/'README.md';path.unlink();path.symlink_to('.gitignore')
        self.approve_destination();self.refuse('only regular README.md')

    def test_source_missing_exact_readme(self):
        self.git(self.src,'mv','README.md','template-readme.md')
        self.git(self.src,'commit','-qm','renamed');self.commit(self.parent)
        self.refuse('exact README.md')

    def test_source_identity_unchanged(self):
        before=self.identity(self.src),self.tree(self.src)
        p=self.invoke();self.assertEqual(0,p.returncode,p.stdout)
        self.assertEqual(before,(self.identity(self.src),self.tree(self.src)))

    def test_missing_source_blob_offline(self):
        (self.src/'src/Missing.cs').write_text('unique missing object fixture')
        self.approve_source()
        blob=self.git(self.src,'rev-parse','HEAD:src/Missing.cs')
        gitdir=Path(self.git(self.src,'rev-parse','--absolute-git-dir'))
        (gitdir/'objects'/blob[:2]/blob[2:]).unlink()
        p=self.refuse(direct=True,env=dict(self.env,GIT_ALLOW_PROTOCOL=''))
        self.assertEqual(1,p.returncode,p.stdout)
        self.assertFalse((self.parent/'.git/team-squared-scaffold-incomplete').exists())

    def test_git_archive_failure(self):
        env=self.wrapper('git','for arg in "$@"; do [[ "$arg" != archive ]] || exit 17; done\nexec /usr/bin/git "$@"\n')
        p=self.refuse(direct=True,env=env)
        self.assertEqual(1,p.returncode,p.stdout)
        self.assertEqual([],list(self.base.glob('team-squared-scaffold*')))

    def test_registry_additional_invalid_rows(self):
        valid=self.placeholder
        for row in [SERVICE+'\t'+valid[:12],SERVICE+'\t'+'z'*40,
                    'goalstats-unknown-service\t'+valid]:
            self.approvals.write_text(row+'\tUser\n');self.commit(self.parent);self.refuse()

    def test_control_characters(self):
        for value in ['goalstats-user\t-service','goalstats-user\x01-service','goalstats-user\r-service']:
            self.refuse('SERVICE must',service=value)

    def test_two_simultaneous_operations(self):
        self.git(self.dest, 'checkout', '--detach')
        entered=self.base/'archive-entered';release=self.base/'archive-release'
        env=self.wrapper('tar','touch "'+str(entered)+'"\nfor attempt in {1..200}; do\n [[ ! -e "'+str(release)+'" ]] || exec /usr/bin/tar "$@"\n sleep 0.1\ndone\nexit 17\n')
        first=subprocess.Popen(['make','scaffold-service','SERVICE='+SERVICE,'DOMAIN=User','DRY_RUN=true'],
                               cwd=self.parent,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        try:
            deadline=time.monotonic()+15
            while not entered.exists() and first.poll() is None and time.monotonic()<deadline:
                time.sleep(0.05)
            self.assertTrue(entered.exists(),'First operation never reached its locked export phase')
            self.refuse('Scaffold lock exists',dry='false')
            self.assertEqual('', self.git(self.dest, 'branch', '--show-current'))
            release.touch()
            output,_=first.communicate(timeout=15)
            self.assertEqual(0,first.returncode,output)
            self.assertEqual(0,self.invoke(dry='true').returncode)
        finally:
            release.touch()
            if first.poll() is None:
                first.communicate(timeout=25)


    def test_domain_validation_and_make_safety(self):
        for domain in ['', 'Template', 'user', 'USER', 'User-Service', 'User_Service', 'User.Service', '../User', 'User$', 'User Service', 'Usér', 'U', 'Abcdefghijklmnop', 'User\n', '$(shell touch injected)', '`touch injected`']:
            self.refuse('DOMAIN must', domain=domain)
        self.assertFalse((self.parent/'injected').exists())

    def test_domain_registry_mismatch(self):
        self.refuse('DOMAIN differs',domain='Match')

    def test_legacy_registry(self):
        self.approvals.write_text(SERVICE+'\t'+self.placeholder+'\n')
        self.commit(self.parent); self.refuse('three tab-separated')

    def test_transformation_refusal_cleans_output(self):
        (self.src/'bad.md').write_text('PrefixTemplateDbContext')
        self.approve_source(); self.refuse('embedded')
        self.assertEqual([],list(self.base.glob('team-squared-scaffold*')))
        self.assertFalse((self.parent/'.git/team-squared-scaffold-incomplete').exists())

    def test_python_unusable(self):
        env=self.wrapper('python3','exit 1\n')
        self.assertEqual(1,self.refuse('Python 3.9+',direct=True,env=env).returncode)
        # Execute the real version probe with a simulated unsupported interpreter.
        env=self.wrapper('python3', '''for arg in "$@"; do probe="$arg"; done
exec /usr/bin/python3 -c 'import sys; sys.version_info=(3,8,0); exec(sys.argv[1])' "$probe"
''')
        self.assertEqual(1,self.refuse('Python 3.9+',direct=True,env=env).returncode)

    def test_missing_python(self):
        toolpath=self.base/'no-python'; toolpath.mkdir()
        for name in ['dirname','git','tar','mktemp','mkdir','rmdir','rm','cp','chmod','find','sort','cmp','cat','tr']:
            (toolpath/name).symlink_to(shutil.which(name,path=self.env['PATH']))
        self.refuse('Missing required tool: Python',direct=True,env=dict(self.env,PATH=str(toolpath)))

    def test_domain_dry_run_summary(self):
        p=self.invoke(dry='true');self.assertEqual(0,p.returncode,p.stdout)
        for text in ['SERVICE='+SERVICE,'DOMAIN=User',self.source_pin,self.placeholder,'PLANNED BRANCH ACTION: NONE','GoalStats.Template -> GoalStats.User','TemplateDbContext -> UserDbContext','goalstats-template -> goalstats-user','goalstats_template -> goalstats_user','RENAME GoalStats.Template.sln -> GoalStats.User.sln']:
            self.assertIn(text,p.stdout)


    def test_two_operations_during_transformation(self):
        self.git(self.dest, 'checkout', '--detach')
        entered=self.base/'transform-entered';release=self.base/'transform-release'
        env=self.wrapper('python3','for arg in "$@"; do\n case "$arg" in --source=*) touch "'+str(entered)+'"; for attempt in {1..200}; do [[ ! -e "'+str(release)+'" ]] || exec /usr/bin/python3 "$@"; sleep 0.1; done; exit 17 ;; esac\ndone\nexec /usr/bin/python3 "$@"\n')
        first=subprocess.Popen(['make','scaffold-service','SERVICE='+SERVICE,'DOMAIN=User','DRY_RUN=true'],cwd=self.parent,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        try:
            deadline=time.monotonic()+15
            while not entered.exists() and first.poll() is None and time.monotonic()<deadline: time.sleep(0.05)
            self.assertTrue(entered.exists(),'Did not reach locked transformation')
            self.refuse('Scaffold lock exists',dry='false')
            self.assertEqual('', self.git(self.dest, 'branch', '--show-current'))
            release.touch();output,_=first.communicate(timeout=15)
            self.assertEqual(0,first.returncode,output)
        finally:
            release.touch()
            if first.poll() is None:first.communicate(timeout=25)

    def test_transformed_ignore_compatibility(self):
        (self.src/'.gitignore').write_text('.env\nbin/\ngoalstats-template-cache/\n')
        self.approve_source()
        (self.dest/'.gitignore').write_text('.env\nbin/\ngoalstats-template-cache/\n')
        self.approve_destination()
        self.refuse('drops or reorders')

if __name__ == '__main__':
    unittest.main()
