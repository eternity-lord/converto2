from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
from app.ui.design_tokens import token
from app.ui.widgets.common import Card, Chart, EmptyTable, Pills, label, button, row
from app.i18n import tr


class Dashboard(QWidget):
    def __init__(self, open_fixer):
        super().__init__()
        box = QVBoxLayout(self)
        box.setContentsMargins(token('space_0'), token('space_0'), token('space_0'), token('space_0'))
        box.setSpacing(int(token('space_4')))
        grid = QGridLayout()
        grid.setSpacing(int(token('space_4')))
        total = Card('Total converted today', True)
        self.converted = label('0.00 GB', 'number')
        self.files = label(f'0 {tr("files · verified output")}', 'muted')
        total.box.addWidget(self.converted)
        total.box.addWidget(self.files)
        grid.addWidget(total, 0, 0)
        insight = Card('TV-Compatibility Check', True)
        insight.box.addWidget(label('One clean frame rate. Every screen.', 'muted'))
        insight.box.addStretch()
        insight.box.addWidget(button('Analyze & Fix MP4s', open_fixer, True))
        grid.addWidget(insight, 1, 0)
        queue = Card('Live queue')
        self.queue_filters = Pills(['All', 'Waiting', 'Done'])
        queue.box.addWidget(self.queue_filters)
        self.queue_table = EmptyTable(0, 2, empty_title='Queue empty',
                                      empty_body='Add or analyze a folder to get started')
        self.queue_table.setEmptyState('Queue empty', 'Add or analyze a folder to get started')
        self.queue_table.setHorizontalHeaderLabels([tr('File'), tr('Status')])
        self.queue_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.queue_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.queue_table.verticalHeader().hide()
        self.queue_table.verticalHeader().setDefaultSectionSize(int(token('table_row_height')))
        self.queue_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.queue_table.setMinimumHeight(int(token('dashboard_table_height')))
        queue.box.addWidget(self.queue_table)
        grid.addWidget(queue, 0, 1, 2, 1)
        performance = Card('Studio performance')
        tiles = QGridLayout()
        tiles.setSpacing(int(token('space_2')))
        self.metrics = {}
        for i, name in enumerate(['Avg speed', 'GPU load', 'CPU load', 'Space saved']):
            tile = Card()
            tile.box.setContentsMargins(token('space_3'), token('space_3'), token('space_3'), token('space_3'))
            value = label('—', 'subtitle')
            tile.box.addWidget(value)
            tile.box.addWidget(label(name, 'muted'))
            tiles.addWidget(tile, i // 2, i % 2)
            self.metrics[name] = value
        performance.box.addLayout(tiles)
        grid.addWidget(performance, 0, 2, 2, 1)
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 3)
        grid.setColumnStretch(2, 3)
        box.addLayout(grid)
        chart_card = Card('Encoding performance')
        self.series = Pills(['Speed', 'CPU', 'GPU'], 'Speed')
        self.ranges = Pills(['1M', '5M', '15M'], '5M')
        chart_card.box.addLayout(row(self.series, None, self.ranges))
        self.chart = Chart(1800)
        chart_card.box.addWidget(self.chart)
        chart_card.setMinimumHeight(int(token('chart_card_height')))
        box.addWidget(chart_card, 1)
        self.queue_filter = 'All'
        self.queue_filters.selected.connect(self.set_filter)
        self.last_jobs = []

    def set_filter(self, value):
        self.queue_filter = value
        self.update_jobs(self.last_jobs)

    def update_jobs(self, jobs):
        self.last_jobs = jobs
        filtered = [j for j in jobs if self.queue_filter == 'All' or j.status == self.queue_filter
                    or (self.queue_filter == 'Done' and j.status == 'TV-Safe ✓')][-8:]
        self.queue_table.setRowCount(len(filtered))
        for i, job in enumerate(filtered):
            self.queue_table.setItem(i, 0, QTableWidgetItem(job.source.name))
            self.queue_table.setItem(i, 1, QTableWidgetItem(f'{tr(job.status)}: {job.data.get("reason","")}  {job.data.get("progress", 0):.0f}%'))
        done = [j for j in jobs if j.status in ('TV-Safe ✓', 'Done') and j.data.get('output')]
        size = sum(j.data.get('size', 0) for j in done)
        self.converted.setText(f'{size / 1e9:.2f} GB')
        self.files.setText(f'{len(done)} {tr("files · verified output")}')
        speeds = [j.data.get('speed', 0) for j in jobs if j.status == 'Encoding']
        self.metrics['Avg speed'].setText(f'{sum(speeds)/len(speeds):.2f}×' if speeds else '—')
        saved = 0
        for job in done:
            try:
                saved += int(job.media.format.get('size') or 0) - job.data.get('size', 0) if job.media else 0
            except OSError:
                pass
        self.metrics['Space saved'].setText(f'{saved / 1e9:+.2f} GB')
