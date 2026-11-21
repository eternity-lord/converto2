"""Manual end-to-end check: real files -> UI queue -> output verification."""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
# Never touch the user's real settings, daily counters or capability cache.
_real_appdata = os.environ.get('APPDATA')
os.environ['APPDATA'] = tempfile.mkdtemp(prefix='edius-e2e-settings-')
if _real_appdata:
    _cache = Path(_real_appdata) / 'EdiusBooster' / 'capabilities.json'
    if _cache.is_file():
        _target = Path(os.environ['APPDATA']) / 'EdiusBooster'
        _target.mkdir(parents=True, exist_ok=True)
        (_target / 'capabilities.json').write_bytes(_cache.read_bytes())

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from app.core.process import capture
from app.core.ffprobe import verify_probe
from app.core.tv_rules import Options, verify
from app.core.settings import Settings
from app.i18n import set_language
from app.ui.theme import apply_theme
from app.ui.main_window import MainWindow


def make_sources(folder):
    folder.mkdir(parents=True, exist_ok=True)
    capture(['ffmpeg', '-v', 'error', '-y',
             '-f', 'lavfi', '-i', 'testsrc2=size=640x360:rate=50:duration=4',
             '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000:duration=4',
             '-vf', "select='if(lt(t,2),not(mod(n,2)),not(mod(n,3)))'", '-fps_mode', 'vfr',
             '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-threads', '2',
             '-c:a', 'aac', '-shortest', str(folder / 'mixed_vfr.mp4')], timeout=60)
    capture(['ffmpeg', '-v', 'error', '-y',
             '-f', 'lavfi', '-i', 'testsrc2=size=640x360:rate=25:duration=3',
             '-f', 'lavfi', '-i', 'sine=frequency=550:sample_rate=96000:duration=3',
             '-c:v', 'libx264', '-pix_fmt', 'yuv422p10le', '-threads', '2',
             '-c:a', 'aac', str(folder / 'tenbit_422.mp4')], timeout=60)
    capture(['ffmpeg', '-v', 'error', '-y',
             '-f', 'lavfi', '-i', 'testsrc2=size=720x576:rate=50:duration=3',
             '-f', 'lavfi', '-i', 'sine=frequency=660:sample_rate=48000:duration=3',
             '-vf', 'tinterlace=mode=interleave_top', '-c:v', 'libx264',
             '-flags', '+ilme+ildct', '-top', '1', '-pix_fmt', 'yuv420p', '-threads', '2',
             '-c:a', 'aac', str(folder / 'interlaced.mp4')], timeout=60)
    capture(['ffmpeg', '-v', 'error', '-y',
             '-f', 'lavfi', '-i', 'color=c=0x315445:size=1920x1080:rate=60000/1001:duration=2.002',
             '-f', 'lavfi', '-i', 'anullsrc=r=96000:cl=5.1', '-t', '2.002',
             '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p', '-threads', '2',
             '-c:a', 'ac3', '-b:a', '384k', str(folder / 'فیلم فارسی ۱۰۸۰.mp4')], timeout=180)
    return folder / 'فیلم فارسی ۱۰۸۰.mp4'


def main():
    root = Path(tempfile.mkdtemp(prefix='edius-e2e-'))
    folder = root / 'ورودی'
    make_sources(folder)
    print('sources:', [p.name for p in folder.iterdir()], flush=True)

    settings = Settings()
    set_language('en')
    app = QApplication(sys.argv[:1])
    apply_theme(app)
    window = MainWindow(settings)
    window.resize(1400, 900)

    options = Options(preset='Universal TV', fps='Auto', output_mode='_TV subfolder',
                      audio='TV-safe', overwrite='Replace')

    def done(tag='finished'):
        results = {}
        for job in window.manager.jobs:
            output = job.data.get('output')
            entry = {'source': job.source.name, 'status': job.status,
                     'reason': job.data.get('reason', ''), 'badge': job.data.get('badge', ''),
                     'pipeline': job.data.get('pipeline', ''),
                     'encoding_status': job.data.get('encoding_status', ''),
                     'analysis_seconds': job.data.get('analysis_seconds'),
                     'output': output}
            if output and Path(output).is_file():
                media = verify_probe(output)
                entry['output_probe'] = {k: media.video.get(k) for k in
                                         ('codec_name', 'profile', 'level', 'pix_fmt', 'width', 'height',
                                          'r_frame_rate', 'avg_frame_rate', 'color_space',
                                          'color_transfer', 'color_primaries', 'color_range',
                                          'codec_tag_string', 'duration', 'start_time')}
                entry['audio'] = [{k: a.get(k) for k in ('codec_name', 'profile', 'channels', 'sample_rate', 'duration', 'start_time')}
                                  for a in media.audio]
                entry['violations'] = verify(media)
                entry['out_size'] = Path(output).stat().st_size
            results[job.source.name] = entry
        report = {'tag': tag, 'safety': window.manager.safety_reason,
                  'paused': window.manager.paused, 'jobs': results,
                  'logs': [f"{r['level']} {r['message'][:200]}" for r in window.logs.records][-25:]}
        Path('e2e_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
        app.quit()

    window.manager.finished.connect(lambda: done('finished'))
    QTimer.singleShot(180000, lambda: done('timeout'))
    QTimer.singleShot(100, lambda: window.scan_folder(str(folder), options, True, window.fixer))
    app.exec()
    window.timer.stop()
    os._exit(0)


if __name__ == '__main__':
    main()
