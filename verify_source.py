"""Validate media integrity, complete ASR windows and reviewed source-to-notes links.

Semantic review records are supplied by an agent/human; this checker cannot
decide whether a screenshot or statement is true on its own.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            value.update(block)
    return value.hexdigest()


def verify(workdir, notes, evidence):
    acquisition = json.loads((workdir / 'acquisition.json').read_text(encoding='utf-8'))
    asr = json.loads((workdir / 'asr_sensevoice_report.json').read_text(encoding='utf-8'))
    segments = json.loads((workdir / 'segments_sensevoice_raw.json').read_text(encoding='utf-8'))
    review = json.loads((evidence / 'content_review.json').read_text(encoding='utf-8'))
    figures = json.loads((evidence / 'figures.json').read_text(encoding='utf-8'))
    notes_text = notes.read_text(encoding='utf-8')
    errors = []
    for media in acquisition['media']:
        if digest(workdir / media['file']) != media['sha256']:
            errors.append(f'Media hash mismatch: {media["file"]}')
        if abs(media['duration'] - acquisition['duration_seconds']) > 3:
            errors.append('Media duration mismatch')
    if acquisition['frame_count'] < math.floor(acquisition['duration_seconds'] / acquisition['sample_interval_seconds']):
        errors.append('Incomplete dense frame extraction')
    if asr['transcription_status'] != 'completed' or abs(asr['last_segment_end'] - acquisition['duration_seconds']) > 1:
        errors.append('ASR did not reach end of media')
    if not segments or segments[0]['start'] != 0 or not asr['nonempty_segments']:
        errors.append('ASR windows are empty or do not start at the beginning')
    if asr['audio_sha256'] != next(m['sha256'] for m in acquisition['media'] if m['file'].startswith('audio.')):
        errors.append('ASR audio provenance mismatch')
    for previous, current in zip(segments, segments[1:]):
        if abs(previous['end'] - current['start']) > 0.01:
            errors.append('Unprocessed audio window')
            break
    if review.get('notes_sha256') != digest(notes):
        errors.append('Review is stale: notes changed')
    if review.get('raw_subtitle_sha256') != digest(workdir / 'audio_sensevoice_raw.srt'):
        errors.append('Review is stale: subtitle track changed')
    for figure in figures:
        path = notes.parent / figure['figure']
        if not path.is_file() or digest(path) != figure['sha256']:
            errors.append(f'Figure hash mismatch: {figure["figure"]}')
        if figure.get('visual_review') != 'PASS':
            errors.append(f'Figure not reviewed: {figure["figure"]}')
        if figure['figure'] not in notes_text:
            errors.append(f'Figure not referenced: {figure["figure"]}')
    timeline_path = evidence / 'timeline_coverage.tsv'
    with timeline_path.open(encoding='utf-8', newline='') as stream:
        windows = list(csv.DictReader(stream, delimiter='\t'))
    expected = math.ceil(acquisition['duration_seconds'] / 300)
    if len(windows) != expected:
        errors.append('Timeline review is incomplete')
    for index, row in enumerate(windows):
        if float(row['start']) != index * 300 or row['status'] not in ('covered', 'context-only'):
            errors.append(f'Unreviewed timeline window {index}')
        if row['notes_section'] not in notes_text:
            errors.append(f'Notes mapping missing: {row["notes_section"]}')
    if review.get('topic_review') != 'PASS':
        errors.append('Semantic topic review is pending')
    report = {
        'status': 'PASS' if not errors else 'FAIL', 'errors': errors,
        'source_url': acquisition['source_url'], 'title': acquisition['title'],
        'duration_seconds': acquisition['duration_seconds'], 'media': acquisition['media'],
        'frame_count': acquisition['frame_count'], 'sample_interval_seconds': acquisition['sample_interval_seconds'],
        'transcription_backend': asr['backend'], 'transcription_windows': len(segments),
        'last_audio_window_end': asr['last_segment_end'], 'timestamp_precision': asr['timestamp_precision'],
        'timeline_review_windows': len(windows), 'reviewed_figures': len(figures),
        'notes_sha256': digest(notes), 'raw_subtitle_sha256': digest(workdir / 'audio_sensevoice_raw.srt'),
        'notes_file': notes.name,
        'review_scope': review['scope'],
        'limitations': ['Not a word-by-word acoustic audit', 'Not an inspection of every video frame',
                        'Classroom software demonstrations were not independently reproduced'],
    }
    evidence.mkdir(exist_ok=True, parents=True)
    (evidence / 'source-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workdir', type=Path)
    parser.add_argument('notes', type=Path)
    parser.add_argument('evidence', type=Path)
    args = parser.parse_args()
    verify(args.workdir.resolve(), args.notes.resolve(), args.evidence.resolve())
