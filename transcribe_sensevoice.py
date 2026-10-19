"""Fast local Chinese ASR in real 20-second audio windows.

Timestamps identify source audio windows, not word-level alignment.
Raw text is retained for review; the program never marks semantic accuracy PASS.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path
from transcribe_audio import stamp


def transcribe(audio, workdir, modeldir, window=20):
    import sherpa_onnx
    import numpy as np
    import imageio_ffmpeg
    workdir.mkdir(parents=True, exist_ok=True)
    pcm_path = workdir / 'audio_16k.f32'
    if not pcm_path.is_file():
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error',
                        '-n', '-i', str(audio), '-ac', '1', '-ar', '16000', '-f', 'f32le',
                        str(pcm_path)], check=True)
    waveform = np.memmap(str(pcm_path), dtype=np.float32, mode='r')
    started = time.monotonic()
    recognizer = sherpa_onnx.OfflineRecognizer.from_sense_voice(
        model=str(modeldir / 'model.int8.onnx'), tokens=str(modeldir / 'tokens.txt'),
        use_itn=True, num_threads=4, language='zh', debug=False)
    records = []
    duration = len(waveform) / 16000
    with (workdir / 'audio_sensevoice_raw.srt').open('w', encoding='utf-8') as srt, \
         (workdir / 'transcript_sensevoice_indexed.txt').open('w', encoding='utf-8') as indexed:
        for position in range(0, len(waveform), 16000 * window):
            start = position / 16000
            end = min(duration, start + window)
            clip = np.array(waveform[position:position + 16000 * window], dtype=np.float32)
            stream = recognizer.create_stream()
            stream.accept_waveform(16000, clip)
            recognizer.decode_stream(stream)
            text = stream.result.text.strip()
            records.append({'id': len(records) + 1, 'start': start, 'end': end,
                            'text': text, 'rms': float(np.sqrt(np.mean(clip * clip)))})
            if text:
                srt.write(f'{len(records)}\n{stamp(start)} --> {stamp(end)}\n{text}\n\n')
                indexed.write(f'[{stamp(start).split(",")[0]}] {text}\n')
            if start % 300 == 0:
                srt.flush()
                indexed.flush()
                print(f'SenseVoice {end:.0f}/{duration:.1f}s; elapsed {time.monotonic()-started:.1f}s', flush=True)
    (workdir / 'segments_sensevoice_raw.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    report = {'backend': 'sherpa-onnx SenseVoice', 'model': modeldir.name,
              'model_sha256': hashlib.sha256((modeldir / 'model.int8.onnx').read_bytes()).hexdigest(),
              'audio_duration': duration, 'segments': len(records),
              'nonempty_segments': sum(bool(r['text']) for r in records),
              'last_segment_end': records[-1]['end'], 'elapsed_seconds': round(time.monotonic()-started, 2),
              'audio_sha256': hashlib.sha256(audio.read_bytes()).hexdigest(),
              'transcription_status': 'completed', 'semantic_review': 'pending',
              'timestamp_precision': f'actual {window}-second audio windows, not word-level timings'}
    (workdir / 'asr_sensevoice_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False), flush=True)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('audio', type=Path)
    parser.add_argument('workdir', type=Path)
    parser.add_argument('modeldir', type=Path)
    args = parser.parse_args()
    transcribe(args.audio.resolve(), args.workdir.resolve(), args.modeldir.resolve())
