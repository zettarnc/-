"""Prepare explicitly selected source frames; requires human semantic review.

The review manifest is specific to BV1kybV6DE47, not a generic scene detector.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
from PIL import Image

SELECTIONS = [
    ('project', 41, '项目目录与可交付产物', (550, 0, 1280, 410)),
    ('learning', 91, '先在脑中实现再比较', (550, 0, 1280, 410)),
    ('init', 151, 'git add 后的暂存区与 git status', (550, 0, 915, 205)),
    ('commit_review', 161, '提交说明与工程实践检查', (550, 0, 915, 410)),
    ('exclude', 231, '不应混入仓库的文件与例外', (550, 0, 1280, 410)),
    ('rule_name', 241, '规则标识的大小写选择', (550, 0, 1280, 410)),
    ('git_visual', 291, '真实仓库的 Git 对象可视化', (550, 0, 1280, 410)),
    ('merge_visual', 311, '分支与合并关系演示', (550, 0, 1280, 410)),
    ('playground', 331, '面向儿童的编程可视化', (550, 0, 1280, 410)),
    ('best_practice', 361, '可恢复、可理解的提交', (550, 0, 1280, 410)),
    ('atomic', 381, '原子变更推进项目', (550, 0, 1280, 410)),
    ('future', 401, 'Agent 产能增长后的版本管理问题', (550, 0, 1280, 410)),
]


def build(workdir, notesdir, evidence):
    notesdir.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)
    manifest = []
    for topic_id, frame_index, topic, box in SELECTIONS:
        frame = workdir / 'frames' / f'frame_{frame_index:05}.jpg'
        output = notesdir / f'fig_{topic_id}.jpg'
        with Image.open(frame) as image:
            if image.size != (1280, 410):
                raise ValueError('Review crop geometry for this source resolution first.')
            image.crop(box).save(output, quality=95)
        start = (frame_index - 1) * 15
        end = min(start + 15, 6013.205)
        manifest.append({'figure': output.name, 'frame': frame.name,
                         'start': start, 'end': end, 'topic': topic, 'crop': list(box),
                         'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                         'source_frame_sha256': hashlib.sha256(frame.read_bytes()).hexdigest(),
                         'visual_review': 'pending'})
    (evidence / 'figures.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    with (evidence / 'figure_manifest.tsv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t')
        writer.writerow(['figure', 'frame', 'start', 'end', 'topic', 'panel'])
        for row in manifest:
            writer.writerow([row['figure'], row['frame'], row['start'], row['end'], row['topic'], 'measured-slide-panel'])
    print(f'{len(manifest)} source figures prepared; semantic review required.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workdir', type=Path)
    parser.add_argument('notesdir', type=Path)
    parser.add_argument('evidence', type=Path)
    args = parser.parse_args()
    build(args.workdir, args.notesdir, args.evidence)
