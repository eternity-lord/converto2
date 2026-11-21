import os
import threading
import time
from collections import deque
from dataclasses import replace
from pathlib import Path
from datetime import date
from PySide6.QtCore import Qt, Signal, QTimer, QByteArray, QPropertyAnimation, QEasingCurve, QPoint, QPointF, QSize
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QStackedWidget, QLineEdit,
                              QSystemTrayIcon, QMenu, QApplication, QGraphicsOpacityEffect, QSizePolicy)
from app.ui.theme import apply_theme
from app.ui.design_tokens import token, duration, motion_easing, reduce_motion
from app.core.capabilities import probe_capabilities, load_cached_capabilities
from app.core.process import tool, capture, terminate_all
from app.core.queue import QueueManager, FolderWatcher, TERMINAL, MAX_JOBS
from app.core.system_tweaks import SystemTweaks, cpu_temperature
from app.ui.widgets.common import GlassWindow, Card, Pills, Toast, label, button, row, scroll, icon, set_rtl
from app.ui.pages.fixer import FixerPage
from app.ui.pages.dashboard import Dashboard
from app.ui.pages.tools import AdvancedPage, TweaksPage, SettingsPage, SupportPage
from app.ui.log_view import LogView
from app.ui.encoding_window import EncodingWindow
from app.ui import dialogs
from app.i18n import tr, set_language

PAGES = ['Dashboard', 'MP4 Profile Fixer', 'HQX Converter', 'QSV Advanced', 'System Tweaks', 'Logs', 'Settings', 'Support']


class Monitor(GlassWindow):
    def __init__(self):
        super().__init__('EDIUS Turbo Monitor · Mohammad Irani',
                         (int(token('monitor_default_width')), int(token('monitor_default_height'))))
        self.resize(int(token('monitor_default_width')), int(token('monitor_default_height')))
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.reading = label('CPU · RAM · Temperature', 'title')
        self.root.addWidget(self.reading)


class MainWindow(GlassWindow):
    capabilities_ready = Signal(object)
    scan_ready = Signal(object)
    metrics_ready = Signal(object)
    temperature_ready = Signal(object)
    background_log = Signal(str, str, str, str)
    cleanup_done = Signal()

    def __init__(self, settings):
        super().__init__('EDIUS Booster · Studio v7',
                         (int(token('window_min_width')), int(token('window_min_height'))))
        self.settings = settings
        self.sidebar_collapsed = bool(settings.get('sidebar_collapsed', False))
        self._sidebar_animation = None
        self._page_animation = None
        self._theme_animation = None
        self.toast = None
        self.closing = False
        self.cleanup_done.connect(QApplication.instance().quit)
        self.resize(int(token('window_default_width')), int(token('window_default_height')))
        geometry = settings.get('geometry')
        if geometry:
            self.restoreGeometry(QByteArray.fromBase64(geometry.encode()))
        self.manager = QueueManager()
        # One-time migration: old Auto=two/GPU or explicit four must not carry unsafe defaults.
        if settings.get('safety_policy_version',0) < 1:
            for key,value in {'safe_mode':True,'high_priority':False,'parallel':'1',
                              'safety_policy_version':1}.items():
                settings.set(key,value)
        parallel = str(settings.get('parallel','1'))
        self.manager.limit = min(3,max(1,int(parallel) if parallel != 'Auto' else 1))
        settings.set('parallel',str(self.manager.limit))
        self.manager.safe_mode = settings.get('safe_mode',True)
        self.manager.high_priority = settings.get('high_priority',False)

        self.encoding = EncodingWindow(self.manager)
        self.monitor = Monitor()
        self.watcher = None
        self.scan_busy = False
        self.metric_busy = False
        self.temperature_busy = False
        self.last_temperature_poll = 0
        self.last_temperature = None
        self.metric_lock = threading.Lock()
        self.metrics_pending = None
        self.temperature_pending = None
        self.cap_busy = False
        self.last_metrics = {}
        self.completed_ids = set()
        self.daily = settings.get('daily', {})
        if self.daily.get('date') != date.today().isoformat():
            self.daily = {'date':date.today().isoformat(),'files':0,'size':0,'saved':0}
        self.telemetry = {'Speed': deque(maxlen=1800), 'CPU': deque(maxlen=1800), 'GPU': deque(maxlen=1800)}
        self.logs = LogView()
        self.content = None
        self.build_ui()
        self.toast = Toast(self)
        self.background_log.connect(self.logs.append)
        self.manager.log.connect(self.logs.append)
        self.manager.changed.connect(self.queue_changed)
        self.scan_ready.connect(self.scanned)
        self.capabilities_ready.connect(self.set_capabilities)
        self.tweaks = None
        self.tweak_busy = False
        self.tweaks_ready = threading.Event()
        def make_tweaks():
            self.tweaks = SystemTweaks(lambda level,msg: self.background_log.emit(level,msg,'',''))
            self.tweaks_ready.set()
        threading.Thread(target=make_tweaks, daemon=True).start()
        self.encoding.completion_action.connect(self.complete)
        self.create_tray()
        self.manager.safety_alert.connect(self.safety_toast)
        self.timer = QTimer(self)
        self.timer.setInterval(int(token('metrics_refresh_interval')))
        self.timer.timeout.connect(self.poll_metrics)
        self.timer.start()
        # A valid cache is available instantly; without it a job started in the first
        # seconds would fall back to the CPU while the hardware probe is still running.
        cached = load_cached_capabilities()
        if cached:
            self.manager.capabilities = cached
            self.set_capabilities(cached, announce=False)
        self.probe_hardware()
        self.manager.finished.connect(lambda: self.tray.showMessage('EDIUS Booster', 'Queue finished. Check logs for verification results.', QSystemTrayIcon.Information, 6000) if self.tray.isVisible() else None)
        self.background_log.emit('INFO','Ready. Select a folder to analyze or convert.','','')

    def build_ui(self):
        if self._sidebar_animation is not None:
            self._sidebar_animation.stop()
        if self._page_animation is not None:
            self._page_animation.stop()
        old = self.content
        # Preserve the bounded log model across the EN/فارسی page rebuild.
        self.logs.setParent(None)
        self.content = QWidget()
        self.content.setObjectName('studioContent')
        outer = QHBoxLayout(self.content)
        outer.setContentsMargins(token('space_2'), token('space_2'), token('space_2'), token('space_2'))
        outer.setSpacing(token('space_4'))

        self.sidebar = Card(surface='glass')
        sidebar_width = int(token('sidebar_collapsed_width') if self.sidebar_collapsed else token('sidebar_width'))
        self.sidebar.setMinimumWidth(sidebar_width)
        self.sidebar.setMaximumWidth(sidebar_width)
        self.sidebar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.sidebar.box.setContentsMargins(token('space_3'), token('space_4'), token('space_3'), token('space_4'))
        self.sidebar.box.setSpacing(token('space_2'))

        brand_header = QWidget()
        brand_layout = QHBoxLayout(brand_header)
        brand_layout.setContentsMargins(token('space_0'), token('space_0'), token('space_0'), token('space_0'))
        brand_layout.setSpacing(token('space_2'))
        brand_size = int(token('icon_l') + token('space_2'))
        self.brand_mark = QLabel()
        self.brand_mark.setPixmap(icon('brand', size=brand_size).pixmap(QSize(brand_size, brand_size)))
        self.brand_mark.setFixedSize(brand_size, brand_size)
        brand_layout.addWidget(self.brand_mark)
        brand_text = QWidget()
        brand_text_layout = QVBoxLayout(brand_text)
        brand_text_layout.setContentsMargins(token('space_0'), token('space_0'), token('space_0'), token('space_0'))
        brand_text_layout.setSpacing(token('space_0'))
        self.brand_title = label('EDIUS Booster', 'subtitle')
        self.brand_subtitle = label('CREATIVE STUDIO / 07', 'caption')
        brand_text_layout.addWidget(self.brand_title)
        brand_text_layout.addWidget(self.brand_subtitle)
        brand_layout.addWidget(brand_text, 1)
        self.sidebar_toggle = button('', self.toggle_sidebar, glyph='collapse', variant='icon')
        self.sidebar_toggle.setAccessibleName(tr('Collapse sidebar'))
        self.sidebar_toggle.setToolTip(tr('Collapse sidebar'))
        brand_layout.addWidget(self.sidebar_toggle)
        self.sidebar.box.addWidget(brand_header)

        self.nav = {}
        glyphs = {
            'Dashboard': 'dashboard', 'MP4 Profile Fixer': 'fixer', 'HQX Converter': 'hqx',
            'QSV Advanced': 'qsv', 'System Tweaks': 'tweaks', 'Logs': 'logs',
            'Settings': 'settings', 'Support': 'support',
        }

        def add_nav(name):
            nav_button = button(tr(name), lambda checked=False, page=name: self.navigate(page),
                                glyph=glyphs[name])
            nav_button.setProperty('nav', True)
            nav_button.setCheckable(True)
            nav_button.setIconSize(QSize(int(token('navigation_icon')), int(token('navigation_icon'))))
            nav_button.setMinimumHeight(int(token('navigation_height')))
            nav_button.setToolTip(tr(name))
            self.sidebar.box.addWidget(nav_button)
            self.nav[name] = nav_button

        for heading, names in (
            ('WORKSPACE', ['Dashboard', 'MP4 Profile Fixer', 'HQX Converter', 'QSV Advanced']),
            ('SYSTEM', ['System Tweaks']),
            ('ACTIVITY', ['Logs']),
        ):
            group = label(heading, 'caption')
            group.setProperty('role', 'caption')
            group.setProperty('navGroup', True)
            self.sidebar.box.addWidget(group)
            for name in names:
                add_nav(name)
            if heading != 'ACTIVITY':
                self.sidebar.box.addSpacing(int(token('space_2')))

        self.sidebar.box.addStretch(1)
        self.queue_button = button('Encoding queue', self.encoding.open, glyph='queue')
        self.queue_button.setToolTip(tr('Encoding queue'))
        self.sidebar.box.addWidget(self.queue_button)
        add_nav('Settings')
        add_nav('Support')
        self.nav_indicator = QWidget(self.sidebar)
        self.nav_indicator.setObjectName('navIndicator')
        self.nav_indicator.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.nav_indicator.setFixedSize(int(token('indicator_width')), int(token('nav_indicator_height')))
        self.nav_indicator.hide()
        outer.addWidget(self.sidebar)

        right = QVBoxLayout()
        right.setContentsMargins(token('space_0'), token('space_0'), token('space_0'), token('space_0'))
        right.setSpacing(token('space_4'))
        welcome = QWidget()
        welcome_box = QVBoxLayout(welcome)
        welcome_box.setContentsMargins(token('space_0'), token('space_0'), token('space_0'), token('space_0'))
        welcome_box.setSpacing(token('space_1'))
        welcome_box.addWidget(label(f'{tr("Welcome,")} Mamad', 'title'))
        welcome_box.addWidget(label('Your studio. Faster, safer, beautifully in sync.', 'muted'))
        self.cap_badge = label('QSV · probing…', 'badge')
        queue_round = button('', self.encoding.open, glyph='queue', variant='icon')
        queue_round.setToolTip(tr('Encoding queue'))
        settings_round = button('', lambda: self.navigate('Settings'), glyph='settings', variant='icon')
        settings_round.setToolTip(tr('Settings'))
        header = row(welcome, None, self.cap_badge, queue_round, settings_round,
                     label(f'Mamad\n{tr("Creator workspace")}', 'muted'))
        right.addLayout(header)

        self.search = QLineEdit()
        self.search.addAction(icon('search'), QLineEdit.LeadingPosition)
        self.search.setPlaceholderText(tr('Search files / filter logs'))
        self.search.setMaximumWidth(int(token('search_max_width')))
        self.tabs = Pills(['Studio', 'Convert', 'Tools'], 'Studio')
        self.tabs.selected.connect(lambda name: self.navigate(
            {'Studio': 'Dashboard', 'Convert': 'MP4 Profile Fixer', 'Tools': 'System Tweaks'}[name]))
        right.addLayout(row(self.tabs, None, self.search))

        self.stack = QStackedWidget()
        self.dashboard = Dashboard(lambda: self.navigate('MP4 Profile Fixer'))
        self.fixer = FixerPage(self.settings, self.manager)
        self.hqx = FixerPage(self.settings, self.manager, True)
        self.advanced = AdvancedPage(self.settings)
        self.tweaks_page = TweaksPage()
        self.settings_page = SettingsPage(self.settings)
        self.settings_page.language_changed.connect(self.change_language)
        self.settings_page.theme_changed.connect(self.change_theme)
        self.settings_page.reprobe.connect(lambda: self.probe_hardware(True))
        self.settings_page.concurrency_changed.connect(lambda value: setattr(self.manager, 'limit', value))
        self.settings_page.execution_changed.connect(self.set_execution_policy)
        self.settings_page.monitor_requested.connect(self.monitor.show)
        self.tweaks_page.apply_requested.connect(self.apply_tweaks)
        self.tweaks_page.restore_requested.connect(self.restore_tweaks)
        self.tweaks_page.monitor_requested.connect(self.monitor.show)
        self.pages = [self.dashboard, self.fixer, self.hqx, self.advanced, self.tweaks_page,
                      self.logs, self.settings_page, SupportPage()]
        for page in self.pages:
            if page is self.logs:
                self.stack.addWidget(page)
            elif page in (self.fixer, self.hqx):
                # Keep the fixed primary action visible while options scroll.
                container = QWidget()
                box = QVBoxLayout(container)
                box.setContentsMargins(token('space_0'), token('space_0'), token('space_0'), token('space_0'))
                box.setSpacing(token('space_2'))
                box.addWidget(scroll(page), 1)
                box.addWidget(page.action_bar)
                self.stack.addWidget(container)
            else:
                self.stack.addWidget(scroll(page))
        for page in (self.fixer, self.hqx):
            page.add_requested.connect(lambda folder, options, start, p=page:
                                       self.scan_folder(folder, options, start, p))
        self.hqx.watch_requested.connect(self.start_watch)
        self.hqx.stop_watch_requested.connect(self.stop_watch)
        right.addWidget(self.stack, 1)
        outer.addLayout(right, 1)
        self.root.addWidget(self.content)
        if old:
            self.root.removeWidget(old)
            old.deleteLater()

        rtl = self.settings.get('language') == 'fa'
        set_rtl(self, rtl)
        # Separate top-level windows are not children, so mirror them explicitly.
        for window in (getattr(self, 'encoding', None), getattr(self, 'monitor', None)):
            if window is not None:
                set_rtl(window, rtl)
        if getattr(self, 'encoding', None) is not None:
            self.encoding.retranslate()
        self._apply_sidebar_state()
        self.advanced.apply_caps(self.manager.capabilities)
        if self.manager.capabilities:
            self.set_capabilities(self.manager.capabilities, announce=False)
        self.navigate('Dashboard')
        self.queue_changed()

    def _apply_sidebar_state(self):
        if not hasattr(self, 'sidebar'):
            return
        collapsed = self.sidebar_collapsed
        self.brand_mark.setVisible(not collapsed)
        self.brand_title.setVisible(not collapsed)
        self.brand_subtitle.setVisible(not collapsed)
        group_labels = self.sidebar.findChildren(QLabel)
        for group in group_labels:
            if group.property('navGroup'):
                group.setVisible(not collapsed)
        for name, nav_button in self.nav.items():
            nav_button.setText('' if collapsed else tr(name))
            nav_button.setProperty('iconOnly', collapsed)
            nav_button.setProperty('rtl', self.layoutDirection() == Qt.LayoutDirection.RightToLeft)
            nav_button.setToolTip(tr(name))
            nav_button.style().unpolish(nav_button)
            nav_button.style().polish(nav_button)
            nav_button.refresh_icon()
        self.queue_button.setText('' if collapsed else tr('Encoding queue'))
        self.queue_button.setProperty('iconOnly', collapsed)
        self.queue_button.style().unpolish(self.queue_button)
        self.queue_button.style().polish(self.queue_button)
        self.queue_button.refresh_icon()
        self.sidebar_toggle._glyph = 'expand' if collapsed else 'collapse'
        self.sidebar_toggle.setProperty('iconGlyph', self.sidebar_toggle._glyph)
        self.sidebar_toggle.setAccessibleName(tr('Expand sidebar' if collapsed else 'Collapse sidebar'))
        self.sidebar_toggle.setToolTip(tr('Expand sidebar' if collapsed else 'Collapse sidebar'))
        self.sidebar_toggle.refresh_icon()
        QTimer.singleShot(0, lambda: self._move_nav_indicator(self.stack.currentIndex(), False))

    def toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed
        self.settings.set('sidebar_collapsed', self.sidebar_collapsed)
        start = self.sidebar.width()
        end = int(token('sidebar_collapsed_width') if self.sidebar_collapsed else token('sidebar_width'))
        self.sidebar.setMinimumWidth(min(start, end))
        self.sidebar.setMaximumWidth(max(start, end))
        self._apply_sidebar_state()
        if self._sidebar_animation is not None:
            self._sidebar_animation.stop()
        if reduce_motion():
            self.sidebar.setFixedWidth(end)
            self._move_nav_indicator(self.stack.currentIndex(), False)
            return
        self._sidebar_animation = QPropertyAnimation(self.sidebar, b'maximumWidth', self)
        self._sidebar_animation.setDuration(duration('slow'))
        x1, y1, x2, y2 = motion_easing('standard')
        curve = QEasingCurve(QEasingCurve.Type.BezierSpline)
        curve.addCubicBezierSegment(QPointF(x1, y1), QPointF(x2, y2), QPointF(1, 1))
        self._sidebar_animation.setEasingCurve(curve)
        self._sidebar_animation.setStartValue(start)
        self._sidebar_animation.setEndValue(end)
        self._sidebar_animation.finished.connect(lambda: self.sidebar.setFixedWidth(end))
        self._sidebar_animation.finished.connect(lambda: self._move_nav_indicator(self.stack.currentIndex(), False))
        self._sidebar_animation.start()

    def _move_nav_indicator(self, index, animate=True):
        if not hasattr(self, 'nav_indicator') or not self.nav_indicator:
            return
        name = PAGES[index] if 0 <= index < len(PAGES) else 'Dashboard'
        target = self.nav.get(name)
        if target is None or not target.isVisible():
            self.nav_indicator.hide()
            return
        point = target.mapTo(self.sidebar, QPoint(0, 0))
        rtl = self.layoutDirection() == Qt.LayoutDirection.RightToLeft
        offset = target.width() - self.nav_indicator.width() - token('space_2') if rtl else token('space_2')
        pos = QPoint(point.x() + int(offset), point.y() +
                     (target.height() - self.nav_indicator.height()) // 2)
        if not self.nav_indicator.isVisible() or reduce_motion() or not animate:
            self.nav_indicator.move(pos)
            self.nav_indicator.show()
            self.nav_indicator.raise_()
            return
        if getattr(self, '_indicator_animation', None) is not None:
            self._indicator_animation.stop()
        self._indicator_animation = QPropertyAnimation(self.nav_indicator, b'pos', self)
        self._indicator_animation.setDuration(duration('slow'))
        self._indicator_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._indicator_animation.setStartValue(self.nav_indicator.pos())
        self._indicator_animation.setEndValue(pos)
        self._indicator_animation.start()

    def navigate(self, name):
        index = PAGES.index(name)
        if self.stack.currentIndex() != index:
            if self._page_animation is not None:
                self._page_animation.stop()
            self.stack.setCurrentIndex(index)
            if not reduce_motion():
                page = self.stack.currentWidget()
                effect = QGraphicsOpacityEffect(page)
                effect.setOpacity(0.0)
                page.setGraphicsEffect(effect)
                animation = QPropertyAnimation(effect, b'opacity', self)
                animation.setDuration(duration('slow'))
                animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                animation.setStartValue(0.0)
                animation.setEndValue(1.0)
                animation.finished.connect(lambda w=page, e=effect:
                                           w.setGraphicsEffect(None) if w.graphicsEffect() is e else None)
                self._page_animation = animation
                QTimer.singleShot(0, animation.start)
        for key, nav_button in self.nav.items():
            nav_button.setChecked(key == name)
            nav_button.refresh_icon()
        active_tab = ('Studio' if name == 'Dashboard' else
                      'Convert' if name in ('MP4 Profile Fixer', 'HQX Converter') else
                      'Tools' if name in ('System Tweaks', 'QSV Advanced', 'Logs', 'Settings', 'Support') else None)
        if active_tab and hasattr(self, 'tabs'):
            self.tabs.value = active_tab
            for key, tab_button in self.tabs.buttons.items():
                tab_button.setChecked(key == active_tab)
        if name == 'Logs':
            # The bounded model only renders while visible; show it without a delay.
            self.logs.refresh()
        QTimer.singleShot(0, lambda: self._move_nav_indicator(index, True))

    def search_changed(self, query):
        if self.stack.currentIndex() == PAGES.index('Logs'):
            self.logs.search.setText(query)
        else:
            self.encoding.open()
            for i, job in enumerate(self.manager.jobs):
                self.encoding.table.setRowHidden(i, query.casefold() not in job.source.name.casefold())

    def change_language(self, value):
        self.settings.set('language',value)
        set_language(value)
        # Preserve the current queue and workers; recreate only page widgets.
        self.build_ui()
        self.logs.retranslate()
        self.logs.refresh()
        self.logs.append('INFO','Language changed. The encoding window uses the chosen language for live status labels.')

    def change_theme(self, mode):
        mode = mode if mode in ('system', 'dark', 'light') else 'system'
        self.settings.set('theme', mode)
        if self._theme_animation is not None:
            self._theme_animation.stop()
        if reduce_motion():
            self.setGraphicsEffect(None)
            apply_theme(QApplication.instance(), mode)
            return
        effect = QGraphicsOpacityEffect(self)
        self._theme_effect = effect
        self.setGraphicsEffect(effect)

        def fade_in(start):
            apply_theme(QApplication.instance(), mode)
            effect.setOpacity(start)
            animation = QPropertyAnimation(effect, b'opacity', self)
            animation.setDuration(duration('slow') // 2)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            animation.setStartValue(start)
            animation.setEndValue(1.0)
            animation.finished.connect(lambda: self.setGraphicsEffect(None)
                                       if self.graphicsEffect() is effect else None)
            self._theme_animation = animation
            animation.start()

        animation = QPropertyAnimation(effect, b'opacity', self)
        animation.setDuration(duration('slow') // 2)
        animation.setEasingCurve(QEasingCurve.Type.InCubic)
        animation.setStartValue(1.0)
        animation.setEndValue(.35)
        animation.finished.connect(lambda: fade_in(.35))
        self._theme_animation = animation
        animation.start()

    def create_tray(self):
        tray_icon = icon('brand', size=int(token('icon_l') + token('space_2')))
        self.setWindowIcon(tray_icon)
        self.tray = QSystemTrayIcon(tray_icon, self)
        menu = QMenu(self)
        menu.addAction('EDIUS Booster', self.showNormal)
        menu.addAction(tr('Encoding queue'), self.encoding.open)
        menu.addAction(tr('Show monitor'), self.monitor.show)
        menu.addAction('Exit', self.close)
        menu.setLayoutDirection(self.layoutDirection())
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self.encoding.open()
                                    if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()

    def probe_hardware(self, force=False):
        if self.cap_busy:
            return
        self.cap_busy = True
        def run():
            try:
                tool('ffprobe')
                result = probe_capabilities(force)
            except Exception as exc:
                result = {'error':str(exc),'codecs':{}}
            self.capabilities_ready.emit(result)
        threading.Thread(target=run, daemon=True).start()

    def set_capabilities(self, caps, announce=True):
        self.cap_busy = False
        self.manager.capabilities = caps
        ready = caps.get('codecs',{}).get('h264_qsv',{}).get('available',False)
        self.cap_badge.setText(tr('QSV ready ✓') if ready else tr('CPU fallback'))
        self.cap_badge.setProperty('tone', 'success' if ready else 'info')
        self.cap_badge.style().unpolish(self.cap_badge)
        self.cap_badge.style().polish(self.cap_badge)
        text = caps.get('error') or caps.get('adapter','') + '\n' + '\n'.join(
            f'{codec}: {"ready" if values["available"] else "unavailable: " + values.get("reason", "self-test failed")}' for codec,values in caps.get('codecs',{}).items())
        text += '\nQSV device: ' + (caps.get('qsv_device') or 'unavailable')
        text += '\n' + ('Haswell: H.264 encode only · 8-bit NV12 · no low_power' if caps.get('haswell') else '8-bit NV12 output')
        text += '\n' + '\n'.join(f'{codec}: ICQ {"supported" if values.get("icq") else "unsupported (VBR)"}' for codec, values in caps.get('codecs', {}).items() if values.get('available'))
        self.settings_page.capabilities.setText(text)
        self.advanced.apply_caps(caps)
        self.fixer.hevc.setEnabled(caps.get('codecs',{}).get('hevc_qsv',{}).get('available',False))
        for index in range(self.hqx.encoder_choice.count()):
            codec = self.hqx.encoder_choice.itemData(index)
            available = codec == 'h264_qsv' or caps.get('codecs',{}).get(codec,{}).get('available',False)
            self.hqx.encoder_choice.model().item(index).setEnabled(available)
        if announce:
            self.logs.append('ERROR' if caps.get('error') else 'INFO', text)
        if caps.get('error'):
            self.fixer.detected.setText(text)

    def scan_folder(self, folder, options, start, page=None):
        if self.scan_busy or self.manager.analysis_running:
            self.logs.append('WARN','A scan / analysis is already running')
            return
        root = Path(folder)
        if not folder or not root.is_dir():
            self.logs.append('ERROR','Please choose an existing folder / لطفاً یک پوشه انتخاب کنید!')
            self.navigate('Logs')
            return
        self.scan_busy = True
        is_hqx = bool(page and page.hqx)
        def scan():
            paths, error = [], ''
            try:
                suffixes = ('.avi','.mov','.mkv') if is_hqx else ('.mp4',)
                output = Path(options.output_folder).resolve() if options.output_folder else None
                for path in root.rglob('*'):
                    if (path.suffix.lower() not in suffixes or '_TV' in path.parts
                            or '.part.' in path.name or path.stem.endswith(('_fixed', options.suffix))
                            or (output and output != root.resolve() and output in path.resolve().parents)):
                        continue
                    paths.append(path)
                    if len(paths) >= MAX_JOBS:
                        break
            except OSError as exc:
                error = str(exc)
            self.scan_ready.emit((paths,options,start,page,error))
        threading.Thread(target=scan,daemon=True).start()

    def scanned(self, result):
        paths, options, start, page, error = result
        self.scan_busy = False
        if error:
            self.logs.append('ERROR',error)
        # A selected fixed rate applies to all waiting files in this batch, including pre-analyzed ones.
        for job in self.manager.jobs:
            if job.status == 'Waiting' and job.source in paths:
                job.options = replace(options)
        self.manager.add_paths(paths,options)
        self.logs.append('INFO',f'{len(paths)} files found / فایل پیدا شد')
        if start:
            self.manager.start()
        elif page and page.property('analyze_next'):
            page.setProperty('analyze_next',False)
            self.manager.analyze()
            self.encoding.open()

    def start_watch(self, folder, options):
        if not folder or not Path(folder).is_dir():
            self.logs.append('ERROR','Select an existing watch folder')
            return
        self.stop_watch()
        self.watcher = FolderWatcher(folder,options.suffix,lambda paths: self.manager.add_paths(paths,options))
        # Queue start is signaled on the GUI thread after incoming entries arrive.
        self.manager.incoming.connect(self.autostart_watch)
        self.watcher.start()
        self.logs.append('INFO',f'Watching recursively: {folder}')

    def autostart_watch(self, _):
        if self.watcher:
            self.manager.start()

    def stop_watch(self):
        if self.watcher:
            self.watcher.stop()
            self.watcher = None
            try:
                self.manager.incoming.disconnect(self.autostart_watch)
            except RuntimeError:
                pass
            self.logs.append('INFO','Folder watch stopped')

    def queue_changed(self):
        self.completed_ids.intersection_update(job.id for job in self.manager.jobs)
        if self.daily.get('date') != date.today().isoformat():
            self.daily = {'date':date.today().isoformat(),'files':0,'size':0,'saved':0}
        changed = False
        for job in self.manager.jobs:
            if job.status in ('TV-Safe ✓','Done') and job.data.get('output') and job.id not in self.completed_ids:
                self.completed_ids.add(job.id)
                self.daily['files'] += 1
                self.daily['size'] += job.data.get('size',0)
                self.daily['saved'] += (int(job.media.format.get('size') or 0) if job.media else 0) - job.data.get('size',0)
                changed = True
        if changed:
            self.settings.set('daily', self.daily)
        self.dashboard.update_jobs(self.manager.jobs)
        self.dashboard.converted.setText(f'{self.daily["size"]/1e9:.2f} GB')
        self.dashboard.files.setText(f'{self.daily["files"]} {tr("files · today")}')
        self.dashboard.metrics['Space saved'].setText(f'{self.daily["saved"]/1e9:+.2f} GB')
        detected = [j.data.get('detected',j.media.badge() if j.media else '') for j in self.manager.jobs if j.media]
        rates = {j.media.fps for j in self.manager.jobs if j.media}
        if len(rates) > 1:
            self.fixer.detected.setText(tr('Mixed frame rates detected across files. Unify all files to: choose a fixed Frame Rate above.'))
        elif detected:
            self.fixer.detected.setText(detected[-1])

    def poll_metrics(self):
        """Collect CPU/RAM/WMI temperature in threads, apply only on the GUI thread.

        Cross-thread Qt signals from these short-lived helper threads could be
        delivered after a window had been destroyed (notably in tests and on a fast
        quit), which crashed the process inside Qt. Handing results over through a
        locked attribute lets the 1 Hz GUI timer apply them safely.
        """
        with self.metric_lock:
            values = self.metrics_pending
            temperature = self.temperature_pending
            self.metrics_pending = None
            self.temperature_pending = None
        if temperature is not None:
            self.temperature_busy = False
            if temperature is not False:
                self.last_temperature = temperature
        if values is not None:
            self.metric_busy = False
            self.set_metrics(values)
        elif not self.metric_busy and not self.closing:
            self.metric_busy = True
            def run():
                import psutil
                sample = {'cpu': psutil.cpu_percent(interval=.1), 'ram': psutil.virtual_memory().percent,
                          'temp': self.last_temperature}
                with self.metric_lock:
                    self.metrics_pending = sample
            threading.Thread(target=run, daemon=True).start()
        # A slow Windows temperature query must never delay the 1Hz CPU/RAM guard.
        now = time.monotonic()
        if not self.temperature_busy and now - self.last_temperature_poll >= 15:
            self.temperature_busy = True
            self.last_temperature_poll = now
            def probe_temperature():
                try:
                    value = cpu_temperature()
                except Exception:
                    value = None
                with self.metric_lock:
                    # False distinguishes "queried, still unavailable" from "not queried".
                    self.temperature_pending = value if value is not None else False
            threading.Thread(target=probe_temperature, daemon=True).start()

    def set_metrics(self, values):
        self.last_metrics = values
        self.manager.observe_resources(values['ram'], values['cpu'])
        self.dashboard.metrics['CPU load'].setText(f'{values["cpu"]:.0f}%')
        self.dashboard.metrics['GPU load'].setText('N/A')
        temperature = f'{values["temp"]:.1f}°C' if values['temp'] is not None else 'N/A'
        self.monitor.reading.setText(f'CPU  {values["cpu"]:.0f}%\nRAM  {values["ram"]:.0f}%\nTemp  {temperature}')
        self.manager.thermal_limit = bool(self.tweaks and self.tweaks.thermal and values['temp'] and
                                          values['temp'] > (80 if self.manager.thermal_limit else 85))
        speeds = [j.data.get('speed',0) for j in self.manager.jobs if j.status == 'Encoding']
        self.telemetry['Speed'].append(sum(speeds)/len(speeds) if speeds else 0)
        self.telemetry['CPU'].append(values['cpu'])
        self.telemetry['GPU'].append(0)
        metric = self.dashboard.series.value
        span = {'1M':60, '5M':300,'15M':900}[self.dashboard.ranges.value]
        self.dashboard.chart.values.clear()
        if metric != 'GPU':
            self.dashboard.chart.values.extend(list(self.telemetry[metric])[-span:])
        self.dashboard.chart.update()

    def set_execution_policy(self, safe_mode, high_priority):
        self.manager.safe_mode = safe_mode
        self.manager.high_priority = high_priority

    def safety_toast(self, reason):
        if self.toast is not None:
            self.toast.show_message(reason, 'warning', timeout=int(token('toast_duration')) * 2)
        if self.tray.isVisible():
            self.tray.showMessage('EDIUS Booster — Safety pause', reason,
                                  QSystemTrayIcon.Warning, 10000)
        else:
            self.cap_badge.setText(tr('Safety pause — see Encoding queue'))
        self.encoding.open()

    def apply_tweaks(self, options):
        if self.tweak_busy or not self.tweaks:
            return
        self.tweak_busy = True
        def run():
            try:
                self.tweaks.apply(options)
            except Exception as exc:
                self.background_log.emit('ERROR',str(exc),'','')
            finally:
                self.tweak_busy = False
        threading.Thread(target=run,daemon=True).start()

    def restore_tweaks(self):
        if self.tweaks:
            threading.Thread(target=self.tweaks.restore,daemon=True).start()

    def complete(self, action):
        if action == 'Do nothing':
            return
        if not any(j.status in ('Done','TV-Safe ✓') for j in self.manager.jobs):
            self.logs.append('WARN','No successful files; finish power action ignored')
            return
        if self.watcher:
            self.logs.append('WARN','Finish action ignored while folder watch is enabled')
            return
        if any(j.status in ('Failed','Blocked','Warning') for j in self.manager.jobs):
            self.logs.append('WARN','Finish action cancelled because some files failed')
            return
        if os.name != 'nt':
            self.logs.append('WARN','Power actions are Windows-only')
            return
        # Explicit selection only. Shutdown has a 60-second cancel window.
        def run():
            if self.tweaks:
                self.tweaks.restore()
            try:
                if action == 'Shut down':
                    capture(['shutdown','/s','/t','60'])
                else:
                    import ctypes
                    ctypes.windll.powrprof.SetSuspendState(False,False,False)
            except Exception as exc:
                self.background_log.emit('ERROR',str(exc),'','')
        threading.Thread(target=run,daemon=True).start()
        self.logs.append('WARN','Shutdown in 60 seconds; run shutdown /a to cancel.' if action == 'Shut down' else 'Entering sleep')

    def closeEvent(self, event):
        self.settings.set('geometry',bytes(self.saveGeometry().toBase64()).decode())
        self.stop_watch()
        if self.closing:
            event.ignore()
            return
        self.closing = True
        self.timer.stop()
        self.manager.stop_all()
        self.hide()
        self.encoding.explicit_close = True
        self.encoding.close()
        self.monitor.close()
        self.tray.hide()
        def cleanup():
            # Keep Qt alive until restoration has completed; never block its event thread.
            terminate_all()
            for job in self.manager.jobs:
                if job.thread and job.thread.is_alive():
                    job.thread.join(timeout=2)
            self.tweaks_ready.wait(timeout=10)
            if self.tweaks:
                self.tweaks.stop_event.set()
                self.tweaks.restore()
            self.cleanup_done.emit()
        threading.Thread(target=cleanup, daemon=True).start()
        event.ignore()
