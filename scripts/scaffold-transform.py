#!/usr/bin/env python3
"""Version 1 identity-only transformation. Never executes template code or uses Git/network."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

POLICY = 1
TOKENS = (b'GoalStats.Template', b'TemplateDbContext', b'goalstats-template', b'goalstats_template')
MATCH = re.compile(b'|'.join(re.escape(t) for t in TOKENS))
TEXT_SUFFIXES = {'.cs', '.csproj', '.sln', '.json', '.yml', '.yaml', '.md', '.sh', '.py'}
TEXT_NAMES = {'Dockerfile', 'Makefile', '.gitignore', '.dockerignore', '.env.example'}

class Refusal(ValueError):
    pass

def validate_domain(domain):
    if not (2 <= len(domain) <= 15 and re.fullmatch(r'[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)*', domain) and domain != 'Template'):
        raise Refusal('DOMAIN must be 2–15 ASCII PascalCase characters, excluding Template and acronyms.')
    return domain

def transform(data, domain):
    replacements = (('GoalStats.' + domain).encode(), (domain + 'DbContext').encode(),
                    ('goalstats-' + domain.lower()).encode(), ('goalstats_' + domain.lower()).encode())
    def replace(match):
        token = match.group(); start, end = match.span()
        before = data[start - 1:start] if start else b''
        if before and re.match(rb'[A-Za-z0-9_]', before):
            raise Refusal('Unexpected embedded identity token: ' + token.decode())
        if token == b'goalstats-template' and before == b'-' and start >= 2 and re.match(rb'[A-Za-z0-9_-]', data[start-2:start-1]):
            raise Refusal('Unexpected embedded kebab token')
        if token == b'GoalStats.Template' and before == b'.':
            raise Refusal('Unexpected embedded namespace token')
        if token == b'TemplateDbContext':
            tail = data[end:]
            suffix = next((s for s in (b'ModelSnapshot', b'Tests') if tail.startswith(s)), b'')
            following = tail[len(suffix):len(suffix) + 1]
            if following and re.match(rb'[A-Za-z0-9_]', following):
                raise Refusal('Unexpected embedded context token')
        elif data[end:end + 1] and re.match(rb'[A-Za-z0-9_]' if token != b'goalstats_template' else rb'[A-Za-z0-9]', data[end:end + 1]):
            raise Refusal('Unexpected embedded identity token: ' + token.decode())
        return replacements[TOKENS.index(token)]
    result = MATCH.sub(replace, data)
    if MATCH.search(result):
        raise Refusal('Residual template identity token')
    return result

def validate_path(path):
    if not re.fullmatch(r'[A-Za-z0-9._/-]+', path) or len(path.encode()) > 900:
        raise Refusal('Unsupported payload filename: ' + path)
    for part in path.split('/'):
        if not part or part in {'.', '..'} or part.endswith('.') or len(part) > 255:
            raise Refusal('Unsafe payload path: ' + path)
        low = part.lower()
        if re.fullmatch(r'(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?', low):
            raise Refusal('Reserved device name: ' + path)
        if low == '.git':
            raise Refusal('Forbidden Git payload: ' + path)
    if path.startswith('-'):
        raise Refusal('Unsafe payload path: ' + path)

def collision_check(paths):
    seen = {}
    for path in paths:
        validate_path(path)
        parts = path.split('/')
        for i in range(1, len(parts) + 1):
            current = '/'.join(parts[:i]); kind = 'file' if i == len(parts) else 'directory'
            previous = seen.get(current.lower())
            if previous and (previous != (current, kind) or kind == 'file'):
                raise Refusal('Transformed path/case/file-directory collision: ' + path)
            seen[current.lower()] = (current, kind)

def anchors(identity='Template'):
    api = 'src/GoalStats.' + identity + '.Api'
    ctx = identity + 'DbContext'
    return {
        'GoalStats.' + identity + '.sln': b'GoalStats.' + identity.encode() + b'.Api',
        api + '/GoalStats.' + identity + '.Api.csproj': b'<Project',
        'tests/GoalStats.' + identity + '.Api.UnitTests/GoalStats.' + identity + '.Api.UnitTests.csproj': b'GoalStats.' + identity.encode() + b'.Api',
        'tests/GoalStats.' + identity + '.Api.IntegrationTests/GoalStats.' + identity + '.Api.IntegrationTests.csproj': b'GoalStats.' + identity.encode() + b'.Api',
        api + '/Infrastructure/Database/' + ctx + '.cs': ('class ' + ctx).encode(),
        api + '/Infrastructure/Database/Migrations/' + ctx + 'ModelSnapshot.cs': (ctx + 'ModelSnapshot').encode(),
        'tests/GoalStats.' + identity + '.Api.IntegrationTests/Infrastructure/Database/' + ctx + 'Tests.cs': (ctx + 'Tests').encode(),
    }

def check_anchors(payload, identity):
    for path, content in anchors(identity).items():
        if path not in payload or content not in payload[path][1]:
            raise Refusal('Missing required identity anchor: ' + path)

def blob_hash(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def read_source(source, manifest):
    payload = {}
    for line in manifest.read_text().splitlines():
        fields = line.split('\t')
        if len(fields) != 3:
            raise Refusal('Malformed source manifest')
        mode, digest, path = fields
        validate_path(path)
        if mode not in {'100644', '100755'} or path in payload:
            raise Refusal('Invalid/duplicate source manifest entry')
        file = source / path
        if not file.is_file() or file.is_symlink():
            raise Refusal('Missing/nonregular source: ' + path)
        data = file.read_bytes()
        if blob_hash(data) != digest or bool(file.stat().st_mode & 0o111) != (mode == '100755'):
            raise Refusal('Source manifest mismatch: ' + path)
        payload[path] = (mode, data)
    collision_check(payload)
    expected = set(payload)
    for path in payload:
        parent = Path(path).parent
        while str(parent) != '.': expected.add(str(parent)); parent = parent.parent
    actual = set()
    for root, dirs, files in os.walk(source, followlinks=False):
        for name in dirs + files:
            path = Path(root) / name
            if path.is_symlink(): raise Refusal('Symlink in source export')
            actual.add(path.relative_to(source).as_posix())
    if actual != expected:
        raise Refusal('Source export paths differ from manifest')
    return payload

def plan(payload, domain):
    validate_domain(domain); check_anchors(payload, 'Template')
    mappings = {path: transform(path.encode(), domain).decode() for path in payload}
    collision_check(payload); collision_check(mappings.values())
    result = {}
    for old, new in mappings.items():
        mode, data = payload[old]
        if Path(old).suffix in TEXT_SUFFIXES or Path(old).name in TEXT_NAMES:
            try: data.decode('utf-8-sig')
            except UnicodeDecodeError: raise Refusal('Invalid UTF-8 text: ' + old)
            if b'\0' in data: raise Refusal('NUL in text: ' + old)
            data = transform(data, domain)
        elif MATCH.search(data) or new != old:
            raise Refusal('Opaque file contains identity or identity-bearing path: ' + old)
        result[new] = (mode, data)
    check_anchors(result, domain)
    return result, mappings

def verify_output(output, expected):
    actual = set()
    expected_paths = set(expected)
    for path in expected:
        parent = Path(path).parent
        while str(parent) != '.': expected_paths.add(str(parent)); parent = parent.parent
    for root, dirs, files in os.walk(output, followlinks=False):
        for name in dirs + files:
            path = Path(root) / name
            if path.is_symlink(): raise Refusal('Symlink in transformed output')
            actual.add(path.relative_to(output).as_posix())
    if actual != expected_paths: raise Refusal('Transformed output paths differ')
    for path, (mode, data) in expected.items():
        file = output / path
        if not file.is_file() or file.read_bytes() != data or stat.S_IMODE(file.stat().st_mode) != (0o755 if mode == '100755' else 0o644):
            raise Refusal('Transformed payload mismatch: ' + path)

def main():
    if sys.version_info < (3, 9):
        print('Scaffold failed: Python 3.9+ is required.', file=sys.stderr); return 1
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--domain', required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--source-manifest', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--source-sha', default='')
    args = parser.parse_args()
    try:
        validate_domain(args.domain)
        if args.source is None:
            return 0
        if any(p is None for p in [args.source_manifest, args.output, args.evidence]):
            raise Refusal('Source, manifest, output and evidence are required together')
        source = args.source.resolve(); output = args.output.resolve()
        if source == output or source in output.parents or output in source.parents or args.output.exists():
            raise Refusal('Output must be a separate new temporary tree')
        original = read_source(source, args.source_manifest)
        expected, mapping = plan(original, args.domain)
        args.output.mkdir(mode=0o700)
        for path, (mode, data) in expected.items():
            file = args.output / path; file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(data); file.chmod(0o755 if mode == '100755' else 0o644)
        # Recompute from the verified source, not from the written output.
        verify_output(args.output, plan(read_source(source, args.source_manifest), args.domain)[0])
        args.evidence.mkdir(exist_ok=True)
        (args.evidence / 'transformed.tsv').write_text(''.join(mode + '\t' + blob_hash(data) + '\t' + path + '\n' for path, (mode, data) in expected.items()))
        (args.evidence / 'mapping.tsv').write_text(''.join(old + '\t' + new + '\n' for old, new in mapping.items()))
        (args.evidence / 'policy.json').write_text(json.dumps({'policy_version': POLICY, 'source_sha': args.source_sha, 'domain': args.domain}, indent=2) + '\n')
        print('DOMAIN=' + args.domain)
        for token, value in zip(TOKENS, ['GoalStats.' + args.domain, args.domain + 'DbContext', 'goalstats-' + args.domain.lower(), 'goalstats_' + args.domain.lower()]):
            print(token.decode() + ' -> ' + value)
        for old, new in mapping.items():
            if old != new: print('  RENAME ' + old + ' -> ' + new)
        return 0
    except Refusal as error:
        print('Scaffold refused: ' + str(error), file=sys.stderr); return 2
    except OSError as error:
        print('Scaffold failed: transformation I/O: ' + str(error), file=sys.stderr); return 1

if __name__ == '__main__':
    sys.exit(main())
