#!/usr/bin/env python3
"""Validate that no hardcoded or weak passwords exist in secrets env files.

Scans all .env files under lib/ and examples/ that are used by secretGenerator
entries and rejects values that match known-weak patterns:
  - The literal '12345678'
  - Any value matching ^[0-9]{8}$ (8-digit numeric)

Keys listed in HEX_KEYS (e.g. HeatAuthEncryptionKey) are validated as
hex-encoded values with a minimum length instead of being checked against
weak-password patterns.

Keys listed in EXTERNALLY_MANAGED_KEYS (e.g. BarbicanSimpleCryptoKEK) are
skipped entirely -- they are injected at deploy time and should not appear
in osp-secrets.env, but if present they are not flagged.

Also warns (but does not fail) if CHANGEME_REQUIRED sentinels are found in
examples/ directories, since those must be replaced before deployment.
"""

import pathlib
import re
import sys

WEAK_PATTERNS = [
    (re.compile(r'^12345678$'), 'literal default password 12345678'),
    (re.compile(r'^\d{8}$'), '8-digit numeric password'),
]

CHANGEME_SENTINEL = 'CHANGEME_REQUIRED'

HEX_KEYS = frozenset({
    'HeatAuthEncryptionKey',
})

EXTERNALLY_MANAGED_KEYS = frozenset({
    'BarbicanSimpleCryptoKEK',
})


def find_env_files(base_dir):
    """Find all .env files under the given directory."""
    return sorted(base_dir.rglob('*.env'))


def _validate_hex_key(value):
    """Return an error reason if value is not valid hex, or None."""
    if not re.fullmatch(r'[0-9a-fA-F]+', value):
        return 'must be a hex-encoded value'
    if len(value) < 32:
        return f'hex key too short ({len(value)} chars, need >= 32)'
    return None


def validate_env_file(env_path, check_sentinels=False):
    """Check an env file for weak password values.

    Returns (errors, warnings) where each is a list of
    (file, line_number, key, value, reason) tuples.
    """
    errors = []
    warnings = []
    with open(env_path) as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip()

            if key in EXTERNALLY_MANAGED_KEYS:
                continue

            if value == CHANGEME_SENTINEL:
                if check_sentinels:
                    warnings.append((
                        env_path, lineno, key, value,
                        'CHANGEME_REQUIRED sentinel must be replaced '
                        'before deployment',
                    ))
                continue

            if key in HEX_KEYS:
                hex_err = _validate_hex_key(value)
                if hex_err:
                    errors.append((env_path, lineno, key, value, hex_err))
                continue

            for pattern, reason in WEAK_PATTERNS:
                if pattern.match(value):
                    errors.append((env_path, lineno, key, value, reason))
                    break

    return errors, warnings


def main():
    repo_root = pathlib.Path(__file__).parent / '..'
    repo_root = repo_root.resolve()

    search_dirs = [
        repo_root / 'lib',
        repo_root / 'examples',
    ]

    examples_dir = repo_root / 'examples'

    all_errors = []
    all_warnings = []

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        check_sentinels = search_dir == examples_dir
        env_files = find_env_files(search_dir)
        for env_file in env_files:
            rel_path = env_file.relative_to(repo_root)
            print(f'Checking: {rel_path}')
            errors, warnings = validate_env_file(
                env_file, check_sentinels=check_sentinels,
            )
            all_errors.extend(errors)
            all_warnings.extend(warnings)

    if all_warnings:
        print(f'\n{len(all_warnings)} CHANGEME_REQUIRED sentinel(s) found:\n')
        for env_path, lineno, key, value, reason in all_warnings:
            rel = env_path.relative_to(repo_root)
            print(f'  WARNING: {rel}:{lineno} {key}={value}')
            print(f'           {reason}')

    if all_errors:
        print(f'\n{len(all_errors)} weak password(s) found:\n')
        for env_path, lineno, key, value, reason in all_errors:
            rel = env_path.relative_to(repo_root)
            print(f'  ERROR: {rel}:{lineno} {key}={value}')
            print(f'         {reason}')
        print(
            f'\n{len(all_errors)} error(s). All password values must be '
            f'securely generated.\n'
            f'See examples/common/README.md for instructions.\n'
            f'Example: openssl rand -hex 16'
        )
        sys.exit(1)
    else:
        print('All secret env files are valid (no weak passwords detected).')
        sys.exit(0)


if __name__ == '__main__':
    main()
