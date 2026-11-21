"""Capture UI screenshots for documentation (real Windows fonts, hidden windows).

Uses a throwaway APPDATA so the user's saved settings and daily counters are untouched.
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt, QTimer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
real_appdata = Path(os.environ.get('APPDATA', Path.home()))
sandbox = Path(tempfile.mkdtemp(prefix='edius-shots-'))
os.environ['APPDATA'] = str(sandbox)
cache = real_appdata / 'EdiusBooster' / 'capabilities.json'
if cache.is_file():
    target = sandbox / 'EdiusBooster'
    target.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(cache, target / 'capabilities.json')

from PySide6.QtWidgets import QApplication  # noqa: E402
from app.core.settings import Settings  # noqa: E402
from app.i18n import set_language  # noqa: E402
from app.ui.theme import apply_theme  # noqa: E402
from app.ui.main_window import MainWindow, PAGES  # noqa: E402

lang = sys.argv[1] if len(sys.argv) > 1 else 'en'
settings = Settings()
settings.set('language', lang)
set_language(lang)
app = QApplication(sys.argv[:1])
apply_theme(app)
w = MainWindow(settings)
w.setAttribute(Qt.WA_DontShowOnScreen, True)
w.resize(1400, 900)
w.show()
out = ROOT / 'docs' / 'screenshots' / lang
out.mkdir(parents=True, exist_ok=True)


def snap():
    for name in PAGES:
        w.navigate(name)
        app.processEvents()
        w.grab().save(str(out / f'{name.replace(" ", "_")}.png'))
    w.encoding.open()
    app.processEvents()
    w.encoding.refresh(force=True)
    app.processEvents()
    w.encoding.grab().save(str(out / 'encoding.png'))
    print('ok', lang, flush=True)
    QTimer.singleShot(50, lambda: os._exit(0))


QTimer.singleShot(3000, snap)
app.exec()
