"""Basic Markdown delivery checks; not a semantic or upstream PDF validator."""
from __future__ import annotations
import argparse
import re
from pathlib import Path
from urllib.parse import unquote


def validate(path: Path) -> list[str]:
    text = path.read_text(encoding='utf-8-sig')
    errors = []
    if not re.search(r'^#\s+\S', text, re.M):
        errors.append('Missing document title')
    if not re.search(r'^##\s+.*(?:来源|参考)', text, re.M):
        errors.append('Missing source/reference section')
    if not re.search(r'https://(?:www\.)?bilibili\.com/|https://(?:www\.)?youtube\.com/|https://youtu\.be/|https://(?:www\.)?(?:x|twitter)\.com/', text):
        errors.append('Missing source video URL')
    opening = None
    prose = []
    for line in text.splitlines():
        match = re.match(r'^\s{0,3}(`{3,}|~{3,})(.*)$', line)
        if match:
            marker, tail = match.groups()
            if opening is None:
                opening = marker
            elif marker[0] == opening[0] and len(marker) >= len(opening) and not tail.strip():
                opening = None
        elif opening is None:
            prose.append(line)
    if opening is not None:
        errors.append('Unclosed fenced code block')
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', '\n'.join(prose)):
        target = target.strip().strip('<>')
        if re.match(r'^[a-zA-Z][\w+.-]*:', target) or target.startswith('#'):
            continue
        relative = unquote(target.split('#', 1)[0].split('?', 1)[0])
        if relative and not (path.parent / relative).exists():
            errors.append(f'Missing local reference: {relative}')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', type=Path, nargs='+')
    args = parser.parse_args()
    failed = False
    for path in args.paths:
        try:
            errors = validate(path)
        except (OSError, UnicodeError) as exc:
            errors = [str(exc)]
        print(f'{"FAIL" if errors else "PASS"}: {path}')
        for error in errors:
            print(f'  - {error}')
        failed |= bool(errors)
    raise SystemExit(1 if failed else 0)
