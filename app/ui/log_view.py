import json
from collections import deque
from datetime import datetime
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QScrollArea, QPlainTextEdit,
                               QApplication, QComboBox)
from app.ui.design_tokens import token
from app.ui.widgets.common import Card, Pills, Toggle, label, button, row
from app.ui import dialogs
from app.i18n import tr


class LogView(QWidget):
    def __init__(self):
        super().__init__()
        self.records = deque(maxlen=400)
        self.level = 'All'
        self.box = QVBoxLayout(self)
        self.box.setContentsMargins(token('space_0'), token('space_0'), token('space_0'), token('space_0'))
        self.box.setSpacing(token('space_3'))
        self.filters = Card('Logs')
        self.pills = Pills(['All', 'Info', 'Warn', 'Error'])
        self.pills.selected.connect(self.set_level)
        self.search = QLineEdit()
        self.search.setPlaceholderText(tr('Search files / filter logs'))
        self.search.textChanged.connect(lambda _: self.refresh())
        self.job_filter = QComboBox()
        self.job_filter.addItem(tr('All files'), '')
        self.job_filter.currentIndexChanged.connect(lambda _: self.refresh())
        self.job_filter.setMinimumWidth(int(token('job_filter_min_width')))
        self.auto = Toggle('Auto-scroll', True)
        self.export_button = button('Export', self.export, variant='secondary')
        self.clear_button = button('Clear', self.clear, variant='ghost')
        self.filters.box.addLayout(row(self.pills, self.search, self.job_filter,
                                       self.export_button, self.clear_button))
        self.filters.box.addWidget(self.auto)
        self.box.addWidget(self.filters)
        self.area = QScrollArea()
        self.area.setWidgetResizable(True)
        self.content = QWidget()
        self.cards = QVBoxLayout(self.content)
        self.cards.setContentsMargins(token('space_0'), token('space_0'), token('space_0'), token('space_0'))
        self.cards.setSpacing(token('space_3'))
        self.cards.addStretch()
        self.area.setWidget(self.content)
        self.box.addWidget(self.area)
        self.dirty = False
        self.timer = QTimer(self)
        self.timer.setInterval(int(token('log_refresh_interval')))
        self.timer.timeout.connect(self.refresh_if_dirty)
        self.timer.start()

    def append(self, level, message, file='', details=''):
        self.records.append(dict(time=datetime.now().isoformat(timespec='seconds'), level=level,
                                 message=message[:2000], file=file, details=details[-32000:]))
        if file and self.job_filter.findData(file) < 0:
            self.job_filter.blockSignals(True)
            self.job_filter.addItem(file if len(file) <= 34 else file[:33] + '…', file)
            self.job_filter.blockSignals(False)
        self.dirty = True

    def retranslate(self):
        self.pills.buttons['All'].setText(tr('All'))
        for value in ('Info', 'Warn', 'Error'):
            self.pills.buttons[value].setText(tr(value))
        self.search.setPlaceholderText(tr('Search files / filter logs'))
        self.auto.setText('Auto-scroll')
        self.export_button.setText(tr('Export'))
        self.clear_button.setText(tr('Clear'))
        self.job_filter.setItemText(0, tr('All files'))
        self.refresh()

    def refresh_if_dirty(self):
        if self.dirty and self.isVisible():
            self.refresh()

    def set_level(self, value):
        self.level = value
        self.refresh()

    def refresh(self):
        self.dirty = False
        position = self.area.verticalScrollBar().value()
        while self.cards.count() > 1:
            item = self.cards.takeAt(0)
            widget = item.widget()
            if widget:
                # deleteLater alone leaves the old card painted until the next event
                # loop pass, which overlaps the rebuilt cards. Detach immediately.
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()
        query = self.search.text().casefold()
        job = self.job_filter.currentData() or ''
        matches = [r for r in self.records
                   if (self.level == 'All' or r['level'] == self.level.upper())
                   and (not job or r['file'] == job)
                   and query in (r['message'] + ' ' + r['file']).casefold()][-100:]
        for record in matches:
            card = Card()
            card.box.setContentsMargins(token('space_4'), token('space_3'), token('space_4'), token('space_3'))
            chip = label(record['level'], 'badge')
            chip.setProperty('tone', {'ERROR': 'danger', 'WARN': 'warning', 'INFO': 'info'}.get(record['level'], 'info'))
            file = label(record['file'], 'muted')
            file.setWordWrap(False)
            file.setMaximumWidth(int(token('log_file_max_width')))
            file.setToolTip(record['file'])
            if len(record['file']) > 42:
                file.setText(record['file'][:41] + '…')
            card.box.addLayout(row(label(record['time'][11:], 'muted'), chip, file, None))
            message = label(record['message'])
            message.setTextFormat(__import__('PySide6.QtCore', fromlist=['Qt']).Qt.PlainText)
            card.box.addWidget(message)
            if record['details']:
                detail = QPlainTextEdit(record['details'])
                detail.setReadOnly(True)
                detail.setMaximumHeight(int(token('log_detail_max_height')))
                detail_font = detail.font()
                detail_font.setFamilies(['JetBrains Mono', 'Cascadia Code', 'Cascadia Mono', 'Consolas', 'DejaVu Sans Mono'])
                detail_font.setPointSize(int(token('font_caption')))
                detail.setFont(detail_font)
                detail.hide()
                toggle = button('Details', lambda checked=False, w=detail: w.setVisible(not w.isVisible()))
                copy = button('Copy', lambda checked=False, r=record: QApplication.clipboard().setText(r['details']))
                card.box.addLayout(row(toggle, copy, None))
                card.box.addWidget(detail)
            self.cards.insertWidget(self.cards.count() - 1, card)
        QTimer.singleShot(0, lambda: self.area.verticalScrollBar().setValue(
            self.area.verticalScrollBar().maximum() if self.auto.isChecked() else position))

    def clear(self):
        self.records.clear()
        self.refresh()

    def export(self):
        name = dialogs.save_file(self, 'edius-log.json', 'JSON (*.json);;Text (*.txt)')
        if name:
            try:
                from pathlib import Path
                text = json.dumps(list(self.records), ensure_ascii=False, indent=2) if name.endswith('.json') else '\n\n'.join(
                    f"{r['time']} [{r['level']}] {r['file']} {r['message']}\n{r['details']}" for r in self.records)
                Path(name).write_text(text, encoding='utf-8')
            except OSError as exc:
                self.append('ERROR', str(exc))
