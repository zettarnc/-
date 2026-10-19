"""Resume a real lecture acquisition -> ASR -> reviewed notes -> PDF workflow.

The writing/review stage belongs to the agent using TASK.md. No script can
replace it by simply marking a checkbox. Missing reviews stop PDF publication.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from acquire_video import acquire
from transcribe_sensevoice import transcribe
from verify_source import verify
from build_latex import build
from validate_markdown import validate


def run(args):
    work = args.workdir.resolve()
    notes = args.notes.resolve()
    evidence = args.evidence.resolve()
    if (work / 'acquisition.json').is_file():
        source = json.loads((work / 'acquisition.json').read_text(encoding='utf-8'))
        if source['source_url'] != args.url:
            raise SystemExit('Work directory belongs to a different URL.')
    else:
        source = acquire(args.url, work, browser=args.browser)
    report_path = work / 'asr_sensevoice_report.json'
    if not report_path.is_file():
        if not args.modeldir:
            raise SystemExit('Acquisition completed. Supply --modeldir with a SenseVoice model directory for ASR.')
        audio = next(m for m in source['media'] if m['file'].startswith('audio.'))
        transcribe(work / audio['file'], work, args.modeldir.resolve())
    if not notes.is_file() or not (evidence / 'content_review.json').is_file():
        raise SystemExit('Source/ASR ready. Agent must write notes and audit source evidence using TASK.md, then rerun.')
    errors = validate(notes)
    if errors:
        raise SystemExit('\n'.join(errors))
    verify(work, notes, evidence)
    build(argparse.Namespace(source=notes, output=args.output, engine=args.engine,
                             engine_path=args.engine_path, pandoc=args.pandoc))
    print('Source checks and PDF conversion PASS. Render and review every PDF page before publishing.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    parser.add_argument('--workdir', type=Path, required=True)
    parser.add_argument('--notes', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, default=Path('evidence'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--modeldir', type=Path)
    parser.add_argument('--browser', choices=['chrome', 'edge', 'firefox', 'brave'])
    parser.add_argument('--engine', choices=['tectonic', 'xelatex'], default='tectonic')
    parser.add_argument('--engine-path')
    parser.add_argument('--pandoc')
    run(parser.parse_args())
