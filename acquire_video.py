"""Acquire one lecture's video, audio, metadata, subtitle candidates and dense frames.

Files stay in the work directory. Public evidence uses sanitized metadata only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def sha256(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def acquire(url, workdir, interval=15, browser=None):
    import av
    import imageio_ffmpeg
    from yt_dlp import YoutubeDL
    workdir.mkdir(parents=True, exist_ok=True)
    base = {'noplaylist': True, 'quiet': False, 'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe()}
    if browser:
        base['cookiesfrombrowser'] = (browser,)
    with YoutubeDL(base) as ydl:
        info = ydl.extract_info(url, download=False)
        if info.get('_type') in ('playlist', 'multi_video') or info.get('entries'):
            raise ValueError('Select exactly one video or Bilibili part before acquisition.')
        safe_info = ydl.sanitize_info(info)
    (workdir / 'metadata.json').write_text(json.dumps(safe_info, ensure_ascii=False, indent=2), encoding='utf-8')
    # Probe with original info, but download via yt-dlp again to refresh signed media URLs.
    for format_spec, stem in [('bestvideo[height<=720]/best', 'video'), ('bestaudio/best', 'audio')]:
        if not list(workdir.glob(f'{stem}.*')):
            with YoutubeDL({**base, 'format': format_spec, 'outtmpl': str(workdir / f'{stem}.%(ext)s')}) as ydl:
                ydl.download([url])
    subtitle_error = None
    if not list(workdir.glob('*.srt')):
        try:
            with YoutubeDL({**base, 'skip_download': True, 'writesubtitles': True,
                            'writeautomaticsub': True, 'subtitleslangs': ['zh.*', 'ai-zh', 'en.*'],
                            'convertsubtitles': 'srt', 'outtmpl': str(workdir / 'captions.%(ext)s'),
                            'postprocessors': [{'key': 'FFmpegSubtitlesConvertor', 'format': 'srt'}]}) as ydl:
                ydl.download([url])
        except Exception as exc:
            subtitle_error = str(exc)
    videos = [p for p in workdir.glob('video.*') if p.suffix.lower() in ('.mp4', '.webm', '.mkv')]
    audios = [p for p in workdir.glob('audio.*') if p.suffix.lower() in ('.m4a', '.webm', '.mp4', '.mp3', '.opus')]
    if len(videos) != 1 or len(audios) != 1:
        raise ValueError('Expected one complete video stream and one complete audio stream.')
    media = []
    for path in [videos[0], audios[0]]:
        with av.open(str(path)) as container:
            duration = container.duration / av.time_base if container.duration else None
            streams = [{'type': s.type, 'codec': s.codec_context.name,
                        **({'width': s.width, 'height': s.height} if s.type == 'video' else {})}
                       for s in container.streams]
        if duration is None or abs(duration - info['duration']) > 3:
            raise ValueError(f'Media duration mismatch: {path.name}')
        media.append({'file': path.name, 'bytes': path.stat().st_size, 'sha256': sha256(path),
                      'duration': duration, 'streams': streams})
    frames = workdir / 'frames'
    frames.mkdir(exist_ok=True)
    expected = int(info['duration'] / interval)
    if len(list(frames.glob('frame_*.jpg'))) < expected:
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error',
                        '-y', '-i', str(videos[0]), '-vf', f'fps=1/{interval}', '-q:v', '3',
                        str(frames / 'frame_%05d.jpg')], check=True)
    report = {'source_url': url, 'video_id': info['id'], 'title': info['title'],
              'uploader': info.get('uploader'), 'duration_seconds': info['duration'],
              'media': media, 'sample_interval_seconds': interval,
              'frame_count': len(list(frames.glob('frame_*.jpg'))),
              'subtitle_candidates': [p.name for p in workdir.glob('captions*.srt')],
              'subtitle_download_error': subtitle_error,
              'source_acquisition': 'PASS', 'semantic_review': 'pending'}
    (workdir / 'acquisition.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    parser.add_argument('workdir', type=Path)
    parser.add_argument('--interval', type=int, default=15)
    parser.add_argument('--browser', choices=['chrome', 'edge', 'firefox', 'brave'])
    args = parser.parse_args()
    if args.interval <= 0:
        parser.error('interval must be positive')
    acquire(args.url, args.workdir.resolve(), args.interval, args.browser)
