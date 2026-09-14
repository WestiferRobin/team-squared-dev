#!/usr/bin/env python3
"""Exact payload verification shared by installation and explicit recovery."""
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat
import sys


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def manifest(data):
    result = {}
    for line in data.decode().splitlines():
        mode, digest, name = line.split('\t')
        parts = name.split('/')
        if (mode not in ('100644', '100755') or len(digest) != 40
                or any(c not in '0123456789abcdef' for c in digest)
                or any(p in ('', '.', '..', '.git') for p in parts)
                or '\\' in name or name.lower() in {p.lower() for p in result}):
            raise ValueError('Invalid or colliding payload manifest path: ' + repr(name))
        result[name] = (mode, digest)
    if not result:
        raise ValueError('Empty payload manifest')
    return result


def verify(directory, expected, allow_build=False):
    directory = Path(directory)
    ancestors = set()
    for name in expected:
        ancestors.update(str(p) for p in PurePosixPath(name).parents if str(p) != '.')
    projects = {str(PurePosixPath(p).parent) for p in expected if p.endswith('.csproj')}
    build_roots = {('/'.join((p, leaf)) if p != '.' else leaf)
                   for p in projects for leaf in ('bin', 'obj')} if allow_build else set()
    # An expected entry always takes precedence over incidental output.
    def incidental(name):
        return any(name == p or name.startswith(p + '/') for p in build_roots)
    actual, extras, bad, artifacts = set(), [], [], []
    def walk(base, prefix=''):
        for entry in os.scandir(base):
            name = prefix + entry.name
            if name == '.git' and allow_build:
                continue
            try:
                info = entry.stat(follow_symlinks=False)
            except FileNotFoundError:
                if incidental(name):
                    continue
                raise ValueError('Filesystem changed during verification: ' + repr(name))
            if stat.S_ISLNK(info.st_mode) or not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                bad.append(name + ' (symlink or unsupported type)')
                continue
            actual.add(name)
            if name in expected:
                mode, digest = expected[name]
                if not stat.S_ISREG(info.st_mode):
                    bad.append(name + ' (not a regular payload file)')
                elif stat.S_IMODE(info.st_mode) != (0o755 if mode == '100755' else 0o644):
                    bad.append(name + ' (mode mismatch)')
                else:
                    fd = os.open(entry.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=base)
                    with os.fdopen(fd, 'rb') as stream:
                        opened = os.fstat(stream.fileno())
                        if (opened.st_dev, opened.st_ino, opened.st_mode) != (info.st_dev, info.st_ino, info.st_mode):
                            raise ValueError('Payload changed during verification: ' + repr(name))
                        if blob(stream.read()) != digest:
                            bad.append(name + ' (content mismatch)')
            elif name in ancestors:
                if not stat.S_ISDIR(info.st_mode):
                    bad.append(name + ' (payload ancestor is not a directory)')
            elif incidental(name):
                if name in build_roots and not stat.S_ISDIR(info.st_mode):
                    bad.append(name + ' (build root is not a directory)')
                else:
                    artifacts.append(name)
            else:
                extras.append(name)
            if stat.S_ISDIR(info.st_mode):
                try:
                    child = os.open(entry.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=base)
                except FileNotFoundError:
                    if incidental(name):
                        continue
                    raise
                try:
                    opened = os.fstat(child)
                    if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                        raise ValueError('Directory changed during verification: ' + repr(name))
                    walk(child, name + '/')
                finally:
                    os.close(child)
    root = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        walk(root)
    finally:
        os.close(root)
    missing = sorted(set(expected) - actual)
    summary = f'missing expected paths: {len(missing)}; unexpected paths: {len(extras)}; payload defects: {len(bad)}; approved incidental entries: {len(artifacts)}'
    if missing or extras or bad:
        details = ['missing: ' + repr(p) for p in missing]
        details += ['unexpected: ' + repr(p) for p in sorted(extras)]
        details += ['defect: ' + repr(p) for p in sorted(bad)]
        raise ValueError('Final payload verification failed; ' + summary + '\n' + '\n'.join(details))
    return summary


if __name__ == '__main__':
    try:
        print(verify(sys.argv[1], manifest(Path(sys.argv[2]).read_bytes()), len(sys.argv) > 3 and sys.argv[3] == 'build-output'))
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)
