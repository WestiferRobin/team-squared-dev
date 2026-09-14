#!/usr/bin/env python3
"""Explicit verification/finalization; never reinstalls or repairs scaffold files."""
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
os.environ.update(GIT_OPTIONAL_LOCKS='0', GIT_NO_LAZY_FETCH='1', GIT_ALLOW_PROTOCOL='', GIT_NO_REPLACE_OBJECTS='1')
spec = importlib.util.spec_from_file_location('scaffold_verify', ROOT/'scripts/scaffold-verify.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(repo, *args):
    result = subprocess.run(['git', '-c', 'core.fsmonitor=false', '-c', 'submodule.recurse=false',
                             '-C', str(repo), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    require(result.returncode == 0, 'Git check failed: ' + args[0])
    return result.stdout


def text(repo, *args):
    return git(repo, *args).decode().strip()


def safe_path(path):
    path = Path(os.path.abspath(path))
    # macOS exposes its system temp area through /var and /tmp aliases.
    # Normalize only those exact system aliases, never user-controlled links.
    for alias, canonical in [('/var', '/private/var'), ('/tmp', '/private/tmp')]:
        if (str(path) == alias or str(path).startswith(alias + '/')) and os.path.realpath(alias) == canonical:
            path = Path(canonical + str(path)[len(alias):])
    for part in [path, *path.parents]:
        require(not part.is_symlink(), 'Symlink in operation path: ' + str(part))
    return path


def read(path):
    path = safe_path(path)
    require(path.is_file(), 'Missing evidence: ' + path.name)
    return path.read_bytes()


def operations(repo):
    for marker in ['MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge',
                   'rebase-apply', 'sequencer', 'BISECT_START']:
        p = Path(text(repo, 'rev-parse', '--git-path', marker))
        if not p.is_absolute(): p = repo/p
        require(not p.exists(), 'Git operation in progress: ' + marker)


def refs(repo):
    return dict(line.split(' ', 1)[::-1] for line in text(repo, 'show-ref').splitlines())


def identity(repo):
    gd = text(repo, 'rev-parse', '--absolute-git-dir')
    result = f'repo {repo}\ngitdir {gd}\n'.encode() + git(repo, 'rev-parse', 'HEAD')
    result += git(repo, 'symbolic-ref', '--quiet', 'HEAD')
    result += git(repo, 'show-ref') + git(repo, 'config', '--local', '--null', '--list')
    log = Path(text(repo, 'rev-parse', '--git-path', 'logs/HEAD'))
    index = Path(text(repo, 'rev-parse', '--git-path', 'index'))
    if not log.is_absolute(): log = repo/log
    if not index.is_absolute(): index = repo/index
    result += (verify.blob(read(log)) if log.exists() else 'no HEAD reflog').encode() + b'\n'
    result += verify.blob(read(index)).encode() + b'\n'
    if (repo/'.git').is_file(): result += verify.blob(read(repo/'.git')).encode() + b'\n'
    return result


def parse_identity(raw):
    header = raw.split(b'\n', 4)
    require(len(header) == 5, 'Malformed identity snapshot')
    repo, gd, head, branch, rest = header
    saved_refs = {}
    while re.match(rb'[0-9a-f]{40} refs/[^\n]+\n', rest):
        row, rest = rest.split(b'\n', 1)
        sha, ref = row.decode().split(' ', 1); saved_refs[ref] = sha
    require(b'\0' in rest, 'Malformed config snapshot')
    config, tail = rest.rsplit(b'\0', 1)
    return repo.decode()[5:], head.decode(), branch.decode(), saved_refs, config+b'\0', tail.splitlines()


def tree(repo, commit):
    rows = []
    for entry in git(repo, 'ls-tree', '-rz', commit).split(b'\0'):
        if not entry: continue
        meta, name = entry.split(b'\t'); mode, kind, sha = meta.decode().split()
        rows.append((mode, kind, sha, name.decode()))
    return rows


def metadata(commit):
    links = {p: sha for m,k,sha,p in tree(ROOT, commit) if m == '160000'}
    # Read committed metadata with Git's parser, never execute or source it.
    result = subprocess.run(['git','config','--blob',commit+':.gitmodules','--get-regexp',
                             r'^submodule\..*\.(path|url)$'], cwd=ROOT, capture_output=True, text=True)
    require(result.returncode == 0, 'Invalid committed submodule metadata')
    values = dict(line.split(None,1) for line in result.stdout.splitlines())
    urls = {}
    for key,path in values.items():
        if key.endswith('.path'): urls[path] = values.get(key[:-5]+'.url')
    return links, urls


ALLOWED_ADVANCEMENT = frozenset({
    'Makefile', 'README.md', 'docs/DEVELOPMENT.md', 'docs/READINESS.md',
    'docs/VALIDATION.md', 'scripts/scaffold-service.sh', 'scripts/scaffold-verify.py',
    'scripts/recover-scaffold.py', 'tests/scaffold_service_test.py',
})
CRITICAL_FILES = ('.gitmodules', 'config/scaffolds.tsv', 'config/components.tsv',
                  'scripts/scaffold-transform.py')


def committed_entries(commit):
    return {p: (mode, kind, sha) for mode, kind, sha, p in tree(ROOT, commit)}


def history_safety(repo):
    require(not text(repo, 'for-each-ref', '--format=%(refname)', 'refs/replace/'),
            'Replace-ref history substitution is unsupported')
    graft = Path(text(repo, 'rev-parse', '--git-path', 'info/grafts'))
    if not graft.is_absolute(): graft = repo/graft
    require(not graft.exists() and not graft.is_symlink(), 'Grafted history is unsupported')
    require(text(repo, 'rev-parse', '--is-shallow-repository') == 'false',
            'Complete local history is required')


def compatible_history(original, current):
    history_safety(ROOT)
    for sha in (original, current):
        require(text(ROOT, 'cat-file', '-t', sha) == 'commit', 'SHA must identify a local commit')
    git(ROOT, 'merge-base', '--is-ancestor', original, current)
    baseline = committed_entries(original)
    frozen = {p: row for p, row in baseline.items() if p in CRITICAL_FILES or row[0] == '160000'}
    require(all(p in frozen for p in CRITICAL_FILES), 'Original critical inputs missing')
    chain = text(ROOT, 'rev-list', '--reverse', original+'..'+current).splitlines()
    previous = original
    for commit in chain:
        parents = text(ROOT, 'show', '-s', '--format=%P', commit).split()
        require(parents == [previous], 'Recovery requires linear history without merges/replacement')
        entries = committed_entries(commit)
        actual = {p: row for p, row in entries.items() if p in CRITICAL_FILES or row[0] == '160000'}
        require(actual == frozen, 'Critical input changed in intervening commit: '+commit)
        changed = git(ROOT, 'diff-tree', '--no-commit-id', '--name-only', '--no-renames', '-r', '-z', previous, commit)
        paths = {p.decode() for p in changed.split(b'\0') if p}
        require(paths <= ALLOWED_ADVANCEMENT, 'Prohibited intervening paths: '+repr(sorted(paths-ALLOWED_ADVANCEMENT)))
        for path in paths:
            require(path not in entries or entries[path][0] in ('100644', '100755'),
                    'Unsupported tooling path type: '+path)
        previous = commit
    require(previous == current, 'Incomplete descendant history')
    return baseline, chain


def parent_worktree(current):
    expected = committed_entries(current)
    staged = {}
    for row in git(ROOT, 'ls-files', '--stage', '-z').split(b'\0'):
        if not row: continue
        meta, path = row.split(b'\t'); mode, sha, stage = meta.decode().split()
        require(stage == '0', 'Unmerged parent index')
        staged[path.decode()] = (mode, sha)
    require(staged == {p: (m, h) for p, (m, k, h) in expected.items()},
            'Parent index differs from approved committed tree')
    for path, (mode, kind, sha) in expected.items():
        if mode == '160000': continue
        require(mode in ('100644', '100755'), 'Unsupported tracked parent file type')
        file = safe_path(ROOT/path)
        require(verify.blob(read(file)) == sha and file.stat().st_mode & 0o7777 ==
                (0o755 if mode == '100755' else 0o644), 'Parent tracked file differs from approved commit: '+path)


def reflog_transition(saved_hash, original, chain):
    path = Path(text(ROOT, 'rev-parse', '--git-path', 'logs/HEAD'))
    if not path.is_absolute(): path = ROOT/path
    data = read(path) if path.exists() else b''
    rows = data.splitlines(keepends=True)
    prefix = b''
    boundary = 0 if saved_hash == b'no HEAD reflog' else None
    for i, row in enumerate(rows):
        prefix += row
        if verify.blob(prefix).encode() == saved_hash:
            boundary = i+1
            break
    require(boundary is not None, 'Original HEAD reflog prefix missing/changed')
    suffix = rows[boundary:]
    # A fast-forward may publish several approved commits in one HEAD transition.
    positions = {sha: i for i, sha in enumerate([original, *chain])}
    previous = original
    for row in suffix:
        fields = row.split(b' ', 2)
        require(len(fields) == 3, 'Malformed HEAD reflog transition')
        old, new = fields[0].decode(), fields[1].decode()
        require(old == previous and new in positions and positions[new] > positions[previous],
                'Unexpected HEAD reflog transitions outside approved forward history')
        previous = new
    require(previous == (chain[-1] if chain else original), 'HEAD reflog does not reach approved tooling')


def original_plan(code, payload, domain):
    # This is reviewed parent code, never template code. A distinct module name
    # prevents the CLI from running; only its pure plan() is invoked, in memory.
    module = types.ModuleType('_original_scaffold_transform')
    exec(compile(code, '<committed scaffold-transform.py>', 'exec'), module.__dict__)
    require(module.POLICY == 1, 'Unsupported original transformation contract')
    return module.plan(payload, domain)


def audit(service, domain, marker, recovery, parent_head, operation_parent):
    policy = json.loads(read(recovery/'policy.json'))
    require(isinstance(policy, dict), 'Malformed operation policy')
    require(policy.get('policy_version') == 1 and policy.get('domain') == domain, 'Operation DOMAIN/version mismatch')
    require(read(recovery/'failed-phase.txt').strip() == b'final verification', 'Operation did not reach final verification')
    saved_parent = parse_identity(read(recovery/'parent.identity'))
    saved_repo, operation_head, saved_branch, saved_refs, saved_config, saved_tail = saved_parent
    require(operation_head == operation_parent, 'OPERATION_PARENT does not match original evidence')
    baseline, chain = compatible_history(operation_parent, parent_head)
    require(saved_repo == str(ROOT), 'Operation parent identity mismatch')
    require(text(ROOT,'symbolic-ref','HEAD') == saved_branch == 'refs/heads/master', 'Parent branch changed')
    require(text(ROOT,'rev-parse','HEAD') == parent_head, 'Parent HEAD changed during recovery')
    operations(ROOT)
    require(text(ROOT, 'rev-parse', 'refs/heads/master') == parent_head and
            text(ROOT, 'rev-parse', 'refs/remotes/origin/master') == parent_head,
            'Approved tooling must equal master and origin/master')
    parent_worktree(parent_head)
    require(not text(ROOT,'status','--porcelain','--untracked-files=all','--ignore-submodules=all'), 'Parent worktree must be clean')
    require(not text(ROOT,'diff','--cached','--name-only'), 'Parent index has staged changes')
    require(git(ROOT,'config','--local','--null','--list') == saved_config, 'Parent config changed')
    links, urls = metadata(parent_head)
    old_links, old_urls = metadata(operation_head)
    require(links == old_links and urls == old_urls, 'Parent gitlinks or canonical URLs changed')
    require(git(ROOT,'show',parent_head+':config/scaffolds.tsv') == git(ROOT,'show',operation_head+':config/scaffolds.tsv'), 'Registry changed')
    require(git(ROOT,'show',parent_head+':config/components.tsv') == git(ROOT,'show',operation_head+':config/components.tsv'), 'Component registry changed')
    approvals = [line.split('\t') for line in git(ROOT,'show',operation_head+':config/scaffolds.tsv').decode().splitlines() if line and not line.startswith('#')]
    require(all(len(row)==3 for row in approvals), 'Invalid approval registry')
    matches = [row for row in approvals if row[0] == service and row[2] == domain]
    require(len(matches)==1, 'SERVICE/DOMAIN not approved')
    approved = matches[0][1]; destination = 'backend/'+service
    source = 'backend/template-goalstats-service'
    require(links.get(destination)==approved, 'Destination pin mismatch')
    require(policy.get('source_sha') == links.get(source), 'Source pin mismatch')
    current_identity = identity(ROOT)
    require(current_identity.split(b'\n', 2)[:2] == read(recovery/'parent.identity').split(b'\n', 2)[:2], 'Parent Git directory changed')
    require(len(saved_tail) == 2, 'Malformed historical parent index/reflog evidence')
    reflog_transition(saved_tail[0], operation_head, chain)
    current_refs = refs(ROOT)
    publication_refs = {'refs/heads/master', 'refs/remotes/origin/master', 'refs/remotes/origin/HEAD'}
    for ref,sha in saved_refs.items():
        expected = parent_head if ref in publication_refs else sha
        if ref in publication_refs:
            require(sha == operation_head, 'Historical publication ref differs from original operation')
        require(current_refs.get(ref)==expected, 'Parent ref changed: '+ref)
    for ref in set(current_refs)-set(saved_refs):
        require(re.fullmatch(r'refs/codex/turn-diffs/captures/[0-9]+/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/base',ref) is not None, 'Unexpected parent ref: '+ref)
        require(text(ROOT,'cat-file','-t',current_refs[ref])=='commit', 'Tooling ref is not a commit')
    dest = safe_path(ROOT/destination); src = safe_path(ROOT/source)
    for repo,path,sha in [(dest,destination,approved),(src,source,links[source])]:
        operations(repo)
        history_safety(repo)
        require(text(repo,'remote','get-url','origin') == urls[path], 'Canonical origin mismatch')
        require(text(repo,'rev-parse','HEAD') == sha, 'Child HEAD changed: '+path)
    require(not text(src,'status','--porcelain','--untracked-files=all'), 'Template is dirty')
    require(text(dest,'symbolic-ref','HEAD') == 'refs/heads/master', 'Destination must remain on master')
    require(text(dest,'rev-parse','refs/heads/master') == approved and text(dest,'rev-parse','refs/remotes/origin/master') == approved, 'Destination master refs changed')
    require(not text(dest,'diff','--cached','--name-only'), 'Destination index has staged changes')
    require(identity(dest) == read(recovery/'dest.installation'), 'Destination Git identity changed')
    transformer_path = 'scripts/scaffold-transform.py'
    transformer_blob = baseline[transformer_path][2]
    original_code = git(ROOT, 'cat-file', 'blob', transformer_blob)
    current_entry = committed_entries(parent_head)[transformer_path]
    require(current_entry == baseline[transformer_path], 'Current transformer differs from original')
    current_code = read(ROOT/transformer_path)
    require(current_code == original_code, 'Current transformer bytes differ from original')
    payload, source_manifest = {}, []
    for mode,kind,sha,path in tree(src,links[source]):
        require(kind=='blob' and mode in ('100644','100755'), 'Unsupported source payload')
        payload[path] = (mode, git(src, 'cat-file', 'blob', sha))
        source_manifest.append(f'{mode}\t{sha}\t{path}\n')
    planned, paths_mapping = original_plan(original_code, payload, domain)
    require((planned, paths_mapping) == original_plan(current_code, payload, domain),
            'Original/current transformation reconstruction mismatch')
    expected = [f'{mode}\t{verify.blob(data)}\t{path}\n' for path,(mode,data) in planned.items()]
    mapping = [old+'\t'+new+'\n' for old,new in paths_mapping.items()]
    reconstructed=''.join(expected).encode(); parsed=verify.manifest(reconstructed)
    for name in ['manifest.tsv','transformed.tsv']:require(read(recovery/name)==reconstructed, 'Reconstructed manifest mismatch: '+name)
    require(read(recovery/'source-manifest.tsv')==''.join(source_manifest).encode(), 'Source manifest mismatch')
    require(read(recovery/'mapping.tsv')==''.join(mapping).encode(), 'Reconstructed mapping mismatch')
    paths=''.join(p+'\n' for p in parsed).encode()
    require(read(recovery/'paths')==paths and read(recovery/'completed.txt')==paths, 'Incomplete or inconsistent completed writes')
    baseline = tree(dest,approved)
    require({p for m,k,h,p in baseline}=={'README.md','.gitignore'}, 'Invalid placeholder baseline')
    for name in ['README.md','.gitignore']:
        require(read(recovery/'original'/name)==git(dest,'show',approved+':'+name), 'Original placeholder backup mismatch')
    result=verify.verify(dest,parsed,True)
    parent_worktree(parent_head)
    require(not text(ROOT,'status','--porcelain','--untracked-files=all','--ignore-submodules=all'),
            'Parent worktree changed during recovery')
    require(identity(dest) == read(recovery/'dest.installation'), 'Destination Git identity changed during verification')
    require(identity(ROOT) == current_identity, 'Parent Git identity changed during verification')
    for repo in (ROOT, dest, src): operations(repo)
    require({p.name for p in marker.iterdir()} == {'recovery-directory'}, 'Operation marker changed')
    require(read(marker/'recovery-directory').decode().strip() == str(recovery) or Path(read(marker/'recovery-directory').decode().strip()).resolve() == recovery, 'Marker changed')
    return ('ORIGINAL OPERATION PARENT SHA: '+operation_head+
            '\nCURRENT RECOVERY TOOLING PARENT SHA: '+parent_head+
            '\nAPPROVED TOOLING SHA MATCH: YES\nORIGINAL IS ANCESTOR: YES'+
            '\nLINEAR HISTORY: YES\nINTERVENING COMMIT SCOPE: PASS'+
            '\nCRITICAL INPUT COMPARISON: PASS\nORIGINAL TRANSFORMER BLOB: '+transformer_blob+
            '\nCURRENT TRANSFORMER MATCH: YES\n'+result)


def main():
    service,domain=os.environ.get('SERVICE',''),os.environ.get('DOMAIN','')
    dry=os.environ.get('DRY_RUN','false')
    original=os.environ.get('OPERATION_PARENT','')
    tooling=os.environ.get('RECOVERY_TOOLING_SHA','')
    for name,value in [('OPERATION_PARENT',original),('RECOVERY_TOOLING_SHA',tooling)]:
        require(re.fullmatch(r'[0-9a-f]{40}',value), name+' must be an explicit full commit SHA')
    require(text(ROOT,'rev-parse','HEAD') == tooling, 'APPROVED TOOLING SHA MATCH: NO; RECOVERY_TOOLING_SHA differs from current HEAD')
    require(re.fullmatch(r'goalstats-[a-z0-9]+(?:-[a-z0-9]+)*-service',service), 'Invalid SERVICE')
    require(re.fullmatch(r'[A-Z][a-zA-Z0-9]{1,14}',domain) and domain!='Template', 'Invalid DOMAIN')
    require(dry in ('true','false'), 'DRY_RUN accepts true or false')
    gd=Path(text(ROOT,'rev-parse','--absolute-git-dir'));marker=safe_path(gd/'team-squared-scaffold-incomplete')
    require(marker.is_dir(), 'No incomplete scaffold operation')
    require({p.name for p in marker.iterdir()}=={'recovery-directory'}, 'Unexpected operation marker contents')
    recovery=safe_path(read(marker/'recovery-directory').decode().strip())
    require(recovery.is_dir() and recovery.name.startswith('team-squared-scaffold.'), 'Invalid recovery directory')
    require(recovery.stat().st_uid==os.getuid() and not recovery.stat().st_mode & 0o077, 'Recovery directory must be private and owned by current user')
    lock=Path('/tmp/team-squared-scaffold-'+verify.blob(str(gd).encode())+'.lock')
    try: lock.mkdir(mode=0o700)
    except FileExistsError: raise ValueError('Scaffold lock exists: '+str(lock))
    try:
        head=text(ROOT,'rev-parse','HEAD')
        require(head == tooling, 'Approved tooling HEAD changed')
        execution_baseline = identity(ROOT)
        print(audit(service,domain,marker,recovery,head,original))
        require(identity(ROOT) == execution_baseline, 'Parent execution baseline changed')
        if dry=='true':
            print('Recovery verified. DRY_RUN: marker, evidence and destination unchanged.')
            return
        # Repeat all checks before the sole mutation; no copying or repair is performed.
        audit(service,domain,marker,recovery,head,original)
        require(identity(ROOT) == execution_baseline, 'Parent execution baseline changed')
        archive=recovery/'finalized-marker'
        require(not archive.exists(), 'Finalized marker archive already exists')
        os.rename(marker,archive)  # Atomic when supported; otherwise fail without deleting marker.
        print('Recovery finalized. Payload/build output unchanged; marker archived at '+str(archive))
    finally:
        lock.rmdir()


if __name__ == '__main__':
    try: main()
    except (ValueError,OSError,KeyError,UnicodeError) as error:
        print('Recovery refused: '+str(error),file=sys.stderr)
        sys.exit(2)
