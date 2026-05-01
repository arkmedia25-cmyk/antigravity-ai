import pathlib, sys, subprocess

sys.path.append('.')
from pipeline.video_build import create_short

long_video = pathlib.Path('test_final.mp4')
if not long_video.exists():
    print("Test video not found!")
    sys.exit(1)

print('Test videosu:', long_video, '| Boyutu:', long_video.stat().st_size // 1024 // 1024, 'MB')

try:
    short = create_short(long_video, slug='test', max_len=10)
    print('SUCCESS: Created short video:', short)
    print('Dosya boyutu:', short.stat().st_size // 1024, 'KB')
except subprocess.CalledProcessError as e:
    print('HATA (ffmpeg):', e)
    print('STDERR:', e.stderr.decode(errors='replace') if e.stderr else 'yok')
except Exception as e:
    print('HATA:', type(e).__name__, str(e))
