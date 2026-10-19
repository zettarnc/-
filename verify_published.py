"""Check that published notes, figures and subtitles match a source review report.

This is the lightweight GitHub CI check. Full media hashing uses verify_source.py
locally because raw video/audio are intentionally not uploaded.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root):
    reports = sorted((root / 'evidence').rglob('source-verification.json'))
    assert reports, 'No source review reports found'
    for report_path in reports:
        verify_lecture(root, report_path.parent)


def verify_lecture(root, evidence):
    report = json.loads((evidence / 'source-verification.json').read_text(encoding='utf-8'))
    notes_name = report.get('notes_file', 'software-repository-management.md')
    assert Path(notes_name).name == notes_name, 'Invalid notes file path'
    notes = root / 'notes' / notes_name
    figures = json.loads((evidence / 'figures.json').read_text(encoding='utf-8'))
    assert report['status'] == 'PASS', 'Source review has not passed'
    assert digest(notes) == report['notes_sha256'], 'Notes changed after source review'
    assert digest(evidence / 'audio_raw.srt') == report['raw_subtitle_sha256'], 'Subtitle provenance mismatch'
    for figure in figures:
        assert digest(notes.parent / figure['figure']) == figure['sha256'], f'Changed figure: {figure["figure"]}'
        assert figure['visual_review'] == 'PASS', f'Figure review missing: {figure["figure"]}'
    print(f'Published source review PASS: {notes.name}, {len(figures)} figures, {report["timeline_review_windows"]} timeline windows')


if __name__ == '__main__':
    verify(Path(__file__).resolve().parent)
