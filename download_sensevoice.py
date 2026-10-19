"""Download the official sherpa-onnx SenseVoice model into an ignored directory."""
from __future__ import annotations
import argparse
import hashlib
import json
import tarfile
import urllib.request
from pathlib import Path

MODEL = 'sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17'
URL = f'https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/{MODEL}.tar.bz2'


def download(root):
    root.mkdir(parents=True, exist_ok=True)
    target = root / MODEL
    if (target / 'model.int8.onnx').is_file() and (target / 'tokens.txt').is_file():
        print(target.resolve())
        return target
    archive = root / f'{MODEL}.tar.bz2'
    urllib.request.urlretrieve(URL, archive)
    with tarfile.open(archive) as bundle:
        bundle.extractall(root, filter='data')
    if not (target / 'model.int8.onnx').is_file() or not (target / 'tokens.txt').is_file():
        raise ValueError('Incomplete model archive')
    (root / 'sensevoice-download.json').write_text(json.dumps({
        'source': URL, 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
        'model_sha256': hashlib.sha256((target / 'model.int8.onnx').read_bytes()).hexdigest(),
    }, indent=2), encoding='utf-8')
    print(target.resolve())
    return target


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, nargs='?', default=Path('work/models'))
    args = parser.parse_args()
    download(args.root)
