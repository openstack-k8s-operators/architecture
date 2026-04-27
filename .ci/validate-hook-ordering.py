#!/usr/bin/env python3
"""Validate numeric prefix ordering on pre/post stage hooks.

When a stage has multiple hooks, run_hook sorts them alphabetically by name.
To guarantee execution order, each hook name must start with a zero-padded
numeric prefix (e.g. "01 Install operator", "02 Create site").

This script checks:
  - If a stage has >1 hook, every hook name starts with a numeric prefix.
  - Prefixes are sequential (01, 02, 03, ...) with no gaps or duplicates.
  - If a stage has exactly 1 hook, a prefix is allowed but not required.
"""

import pathlib
import re
import sys

import yaml

PREFIX_RE = re.compile(r'^(\d+)\s+')

def validate_hooks(hooks, stage_label):
    """Validate a list of hooks. Returns list of error strings."""
    errors = []
    if not hooks or len(hooks) < 2:
        return errors

    prefixes = []
    for hook in hooks:
        name = hook.get('name', '<unnamed>')
        m = PREFIX_RE.match(name)
        if not m:
            errors.append(
                f'{stage_label}: hook "{name}" is missing a numeric prefix '
                f'(required when stage has {len(hooks)} hooks)'
            )
        else:
            if not m.group(1).startswith('0') and len(m.group(1)) < 2:
                errors.append(
                    f'{stage_label}: hook "{name}" prefix must be zero-padded '
                    f'(e.g. "01" not "1")'
                )
            prefixes.append((int(m.group(1)), name))

    if errors:
        return errors

    prefixes.sort(key=lambda x: x[0])
    seen = set()
    for num, name in prefixes:
        if num in seen:
            errors.append(
                f'{stage_label}: duplicate prefix {num:02d} on hook "{name}"'
            )
        seen.add(num)

    nums = [p[0] for p in prefixes]
    expected = list(range(nums[0], nums[0] + len(nums)))
    if nums != expected:
        errors.append(
            f'{stage_label}: prefixes {nums} are not sequential '
            f'(expected {expected})'
        )

    return errors


def validate_file(path):
    """Validate all stages in one automation vars file."""
    errors = []
    with open(path) as fh:
        content = yaml.safe_load(fh)

    for scenario_name, scenario in content.get('vas', {}).items():
        for i, stage in enumerate(scenario.get('stages', [])):
            stage_name = stage.get('name', f'stage-{i}')
            label = f'{path.name} > {scenario_name} > {stage_name}'

            for hook_type in ('pre_stage_run', 'post_stage_run'):
                hooks = stage.get(hook_type)
                if hooks:
                    errs = validate_hooks(hooks, f'{label} > {hook_type}')
                    errors.extend(errs)

    return errors


def main():
    src_dir = pathlib.Path(__file__).parent / '..' / 'automation' / 'vars'
    all_errors = []

    for f in sorted(src_dir.glob('*.yaml')):
        all_errors.extend(validate_file(f))

    if all_errors:
        print('Hook ordering errors found:\n')
        for err in all_errors:
            print(f'  ERROR: {err}')
        print(f'\n{len(all_errors)} error(s) found.')
        sys.exit(1)
    else:
        print('All hook orderings are valid.')
        sys.exit(0)


if __name__ == '__main__':
    main()
