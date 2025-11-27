#!/usr/bin/env python3
"""Trim trailing blank lines from Python files and ensure a single newline at EOF.

Skips virtualenv and migration directories.
"""
from pathlib import Path

EXCLUDE_DIRS = {"migrations", ".venv", "venv"}

def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    return any(ex in parts for ex in EXCLUDE_DIRS)


def main():
    repo = Path('.').resolve()
    changed = []
    for p in repo.rglob('*.py'):
        # Skip files inside excluded directories
        if should_skip(p):
            continue
        try:
            s = p.read_text(encoding='utf-8')
        except Exception:
            continue
        new = s.rstrip() + '\n'
        if s != new:
            p.write_text(new, encoding='utf-8')
            changed.append(str(p))
    if changed:
        print('Trim complete. Modified files:')
        for f in changed:
            print(' -', f)
    else:
        print('Trim complete. No files changed.')


if __name__ == '__main__':
    main()
