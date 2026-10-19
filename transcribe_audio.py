"""Local timestamped transcription with progress and explicit completeness report."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path


def stamp(value):
    millis = round(value * 1000)
    hours, millis = divmod(millis, 3600000)
    minutes, millis = divmod(millis, 60000)
    seconds, millis = divmod(millis, 1000)
    return f'{hours:02}:{minutes:02}:{seconds:02},{millis:03}'


def transcribe(audio, workdir, model_name='small', threads=6, batch_size=8):
    from faster_whisper import WhisperModel, BatchedInferencePipeline
    workdir.mkdir(parents=True, exist_ok=True)
    model_dir = workdir.parent / 'models'
    model_dir.mkdir(exist_ok=True)
    print(f'Loading local ASR model: {model_name}', flush=True)
    started = time.monotonic()
    model = WhisperModel(model_name, device='cpu', compute_type='int8',
                         cpu_threads=threads, download_root=str(model_dir))
    engine = BatchedInferencePipeline(model=model)
    # Decode using bundled FFmpeg. This avoids the removed metadata_errors
    # argument in PyAV 19 used by faster-whisper 1.2.1's audio path decoder.
    import imageio_ffmpeg
    import numpy as np
    pcm_path = workdir / 'audio_16k.f32'
    if not pcm_path.is_file():
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error',
                        '-n', '-i', str(audio), '-ac', '1', '-ar', '16000', '-f', 'f32le',
                        str(pcm_path)], check=True)
    waveform = np.memmap(str(pcm_path), dtype=np.float32, mode='r')
    segments, info = engine.transcribe(
        waveform, language='zh', beam_size=3, batch_size=batch_size,
        vad_filter=True, condition_on_previous_text=False,
        initial_prompt='简体中文技术讲座。Git, GitHub, repository, commit, tree, blob, HEAD, index, merge, rebase, gitv, bisect, blame, AGENTS.md, Conventional Commits。')
    print(f'Audio duration: {info.duration:.3f}s; model loaded after {time.monotonic()-started:.1f}s', flush=True)
    records = []
    last_progress = -300
    with (workdir / 'audio_raw.srt').open('w', encoding='utf-8') as srt, \
         (workdir / 'transcript_indexed.txt').open('w', encoding='utf-8') as indexed:
        for number, segment in enumerate(segments, 1):
            item = {'id': number, 'start': segment.start, 'end': segment.end,
                    'text': segment.text.strip(), 'avg_logprob': segment.avg_logprob,
                    'no_speech_prob': segment.no_speech_prob}
            records.append(item)
            srt.write(f'{number}\n{stamp(segment.start)} --> {stamp(segment.end)}\n{item["text"]}\n\n')
            indexed.write(f'[{stamp(segment.start).split(",")[0]}] {item["text"]}\n')
            if segment.end - last_progress >= 180:
                print(f'ASR progress: {segment.end:.1f}/{info.duration:.1f}s; {number} segments; elapsed {time.monotonic()-started:.1f}s', flush=True)
                srt.flush()
                indexed.flush()
                last_progress = segment.end
    (workdir / 'segments_raw.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    report = {'backend': 'faster-whisper', 'model': Path(model_name).name, 'compute_type': 'int8',
              'audio_duration': info.duration, 'segments': len(records),
              'last_segment_end': records[-1]['end'] if records else 0,
              'elapsed_seconds': round(time.monotonic()-started, 2),
              'audio_sha256': hashlib.sha256(audio.read_bytes()).hexdigest(),
              'transcription_status': 'completed' if records else 'failed',
              'semantic_review': 'pending', 'verbatim_accuracy': 'not_guaranteed'}
    (workdir / 'asr_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False), flush=True)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('audio', type=Path)
    parser.add_argument('workdir', type=Path)
    parser.add_argument('--model', default='small')
    parser.add_argument('--threads', type=int, default=6)
    parser.add_argument('--batch-size', type=int, default=8)
    args = parser.parse_args()
    os.environ.setdefault('HF_HUB_DISABLE_XET', '1')
    transcribe(args.audio.resolve(), args.workdir.resolve(), args.model, args.threads, args.batch_size)
