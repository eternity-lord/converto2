"""Qt styling and theme selection for the Obsidian Glass design system."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette

from app.ui.design_tokens import (
    active_theme,
    set_active_theme,
    set_reduce_motion,
    token,
    tokens,
    windows_reduce_motion,
)


def asset(*parts):
    """Absolute path to a bundled asset, in both source and PyInstaller builds."""
    import sys
    base = Path(sys._MEIPASS) if getattr(sys, '_MEIPASS', None) else Path(__file__).resolve().parents[2]
    return base.joinpath('assets', *parts)


def resolve_theme(mode='system', app=None):
    if mode in ('dark', 'light'):
        return mode
    try:
        hints = app.styleHints() if app is not None else None
        scheme = hints.colorScheme() if hints is not None else Qt.ColorScheme.Unknown
        return 'light' if scheme == Qt.ColorScheme.Light else 'dark'
    except (AttributeError, RuntimeError):
        return 'dark'


def _gradient(t, diagonal=True):
    end_x, end_y = ('1', '1') if diagonal else ('1', '0')
    return (f"qlineargradient(x1:0, y1:0, x2:{end_x}, y2:{end_y}, "
            f"stop:0 {t['accent_gradient_start']}, stop:1 {t['accent_gradient_end']})")


def build_qss(t=None):
    """Generate the whole widget sheet from design tokens, never local literals."""
    t = t or tokens()
    px = lambda name: f"{t[name]}px"
    gradient = _gradient(t)
    gradient_horizontal = _gradient(t, diagonal=False)
    return f'''
* {{
    color: {t['text_primary']};
    font-size: {px('font_body')};
    selection-background-color: {t['accent']};
    selection-color: {t['text_on_accent']};
}}
QWidget {{ background: transparent; }}
QWidget:disabled {{ color: {t['text_disabled']}; }}
QToolTip {{
    background: {t['tooltip_surface']}; color: {t['text_primary']};
    border: {px('border_width')} solid {t['border_default']}; border-radius: {px('radius_sm')};
    padding: {px('space_2')} {px('space_3')};
}}
QLabel {{ background: transparent; color: {t['text_primary']}; }}
QLabel[role="caption"], QLabel[role="muted"] {{
    color: {t['text_tertiary']}; font-size: {px('font_caption')};
}}
QLabel[role="secondary"] {{ color: {t['text_secondary']}; }}
QLabel[role="title"] {{ font-size: {px('font_title')}; font-weight: {t['weight_semibold']}; }}
QLabel[role="subtitle"] {{ font-size: {px('font_subtitle')}; font-weight: {t['weight_semibold']}; }}
QLabel[role="display"] {{ font-size: {px('font_display')}; font-weight: {t['weight_bold']}; }}
QLabel[role="number"] {{ font-size: {px('font_number')}; font-weight: {t['weight_bold']}; }}
QLabel[role="mono"] {{ color: {t['text_secondary']}; }}
QLabel[role="positive"] {{ color: {t['success']}; }}
QLabel[role="warning"] {{ color: {t['warning']}; }}
QLabel[role="danger"] {{ color: {t['danger']}; }}
QLabel[role="info"] {{ color: {t['info']}; }}
QLabel[role="preview"] {{
    background: {t['preview_surface']}; border: {px('border_width')} solid {t['border_subtle']};
    border-radius: {px('radius_md')}; color: {t['text_tertiary']};
}}
QLabel[role="badge"] {{
    background: {t['accent_soft']}; color: {t['accent_hover']};
    border: {px('border_width')} solid {t['border_subtle']}; border-radius: {px('radius_full')};
    padding: {px('space_1')} {px('space_3')}; font-size: {px('font_caption')};
}}
QLabel[role="badge"][tone="success"] {{ background: {t['success_soft']}; color: {t['success']}; }}
QLabel[role="badge"][tone="warning"] {{ background: {t['warning_soft']}; color: {t['warning']}; }}
QLabel[role="badge"][tone="danger"] {{ background: {t['danger_soft']}; color: {t['danger']}; }}
QLabel[role="badge"][tone="info"] {{ background: {t['info_soft']}; color: {t['info']}; }}

QPushButton {{
    min-height: {px('button_m')}; padding: 0 {px('button_padding_x')};
    background: {t['bg_layer3']}; color: {t['text_primary']};
    border: {px('border_width')} solid {t['border_default']}; border-radius: {px('radius_sm')};
    font-weight: {t['weight_medium']};
}}
QPushButton:hover {{ background: {t['bg_hover']}; border-color: {t['border_strong']}; }}
QPushButton:pressed {{ background: {t['bg_pressed']}; }}
QPushButton:focus {{ border: {px('focus_width')} solid {t['accent_hover']}; }}
QPushButton:disabled {{
    color: {t['text_disabled']}; background: {t['bg_layer2']};
    border-color: {t['border_subtle']};
}}
QPushButton[buttonSize="S"] {{ min-height: {px('button_s')}; max-height: {px('button_s')}; padding: 0 {px('space_3')}; }}
QPushButton[buttonSize="M"] {{ min-height: {px('button_m')}; }}
QPushButton[buttonSize="L"] {{ min-height: {px('button_l')}; max-height: {px('button_l')}; }}
QPushButton[loading="true"] {{ color: transparent; }}
QPushButton[variant="primary"], QPushButton[primary="true"] {{
    background: {gradient}; color: {t['text_on_accent']}; border-color: {t['accent']}; font-weight: {t['weight_semibold']};
}}
QPushButton[variant="primary"]:hover, QPushButton[primary="true"]:hover {{
    background: {gradient_horizontal}; border-color: {t['accent_hover']}; color: {t['text_on_accent']};
}}
QPushButton[variant="primary"]:pressed, QPushButton[primary="true"]:pressed {{
    background: {t['accent_pressed']}; border-color: {t['accent_pressed']};
}}
QPushButton[variant="danger"] {{
    background: {t['danger_soft']}; color: {t['danger']}; border-color: {t['danger_border']};
}}
QPushButton[variant="danger"]:hover {{
    background: {t['danger']}; color: {t['text_on_accent']}; border-color: {t['danger']};
}}
QPushButton[variant="danger"]:pressed {{ background: {t['danger']}; }}
QPushButton[variant="ghost"] {{ background: transparent; color: {t['text_secondary']}; border-color: transparent; }}
QPushButton[variant="ghost"]:hover {{ background: {t['ghost_hover']}; color: {t['text_primary']}; }}
QPushButton[variant="ghost"]:pressed {{ background: {t['ghost_pressed']}; }}
QPushButton[variant="segmented"] {{
    min-height: {px('button_s')}; padding: 0 {px('space_3')};
    background: transparent; color: {t['text_secondary']}; border-color: transparent;
}}
QPushButton[variant="segmented"]:hover {{ background: {t['bg_hover']}; color: {t['text_primary']}; }}
QPushButton[variant="segmented"]:checked {{
    background: {t['accent_soft']}; color: {t['accent_hover']}; border-color: {t['border_subtle']};
}}
QPushButton[nav="true"] {{
    min-height: {px('navigation_height')}; padding: 0 {px('space_3')};
    text-align: left; background: transparent; border-color: transparent; border-radius: {px('radius_sm')};
}}
QPushButton[nav="true"]:hover {{ background: {t['bg_hover']}; color: {t['text_primary']}; }}
QPushButton[nav="true"]:checked {{
    background: {t['accent_soft']}; color: {t['text_primary']}; border-color: {t['border_subtle']};
}}
QPushButton[nav="true"][rtl="true"] {{ text-align: right; }}
QPushButton[iconOnly="true"] {{
    min-width: {px('button_m')}; max-width: {px('button_m')}; padding: 0; text-align: center;
}}
QPushButton[nav="true"][iconOnly="true"] {{ min-width: {px('button_m')}; max-width: {px('button_m')}; }}
QPushButton[variant="icon"], QPushButton[iconOnly="true"] {{
    min-width: {px('button_m')}; max-width: {px('button_m')}; min-height: {px('button_m')};
    max-height: {px('button_m')}; padding: 0; border-radius: {px('radius_sm')};
}}
QPushButton[variant="titlebar"] {{
    min-width: {px('titlebar_button_width')}; max-width: {px('titlebar_button_width')};
    min-height: {px('titlebar_button_height')}; max-height: {px('titlebar_button_height')};
    background: transparent; border-color: transparent; border-radius: {px('radius_sm')}; padding: 0;
}}
QPushButton[variant="titlebar"]:hover {{ background: {t['ghost_hover']}; }}
QPushButton[windowClose="true"]:hover {{ background: {t['window_close_hover']}; color: {t['close_hover_text']}; }}
QPushButton[windowClose="true"]:pressed {{ background: {t['window_close_hover']}; }}
QPushButton[variant="collapse"] {{ min-height: {px('button_s')}; background: transparent; border-color: transparent; }}

QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    min-height: {px('input_height')}; padding: 0 {px('input_padding_x')};
    background: {t['bg_layer3']}; color: {t['text_primary']};
    border: {px('border_width')} solid {t['border_default']}; border-radius: {px('radius_sm')};
    selection-background-color: {t['accent']}; selection-color: {t['text_on_accent']};
}}
QPlainTextEdit, QTextEdit {{ padding: {px('space_2')} {px('input_padding_x')}; }}
QLineEdit:hover, QPlainTextEdit:hover, QTextEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {{
    border-color: {t['border_strong']};
}}
QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QComboBox:focus {{
    border: {px('focus_width')} solid {t['accent']}; background: {t['bg_layer2']};
}}
QLineEdit:disabled, QPlainTextEdit:disabled, QTextEdit:disabled,
QSpinBox:disabled, QDoubleSpinBox:disabled, QComboBox:disabled {{
    color: {t['text_disabled']}; background: {t['bg_layer2']}; border-color: {t['border_subtle']};
}}
QComboBox {{ padding-right: {px('space_6')}; }}
QComboBox[rtl="true"] {{ padding-left: {px('space_6')}; padding-right: {px('input_padding_x')}; }}
QComboBox::drop-down {{
    subcontrol-origin: padding; subcontrol-position: top right; width: {px('space_6')};
    border: 0; border-top-right-radius: {px('radius_sm')}; border-bottom-right-radius: {px('radius_sm')};
}}
QComboBox[rtl="true"]::drop-down {{
    subcontrol-position: top left; border-top-left-radius: {px('radius_sm')};
    border-bottom-left-radius: {px('radius_sm')}; border-top-right-radius: 0; border-bottom-right-radius: 0;
}}
QComboBox QAbstractItemView {{
    background: {t['menu_surface']}; color: {t['text_primary']};
    border: {px('border_width')} solid {t['border_default']}; border-radius: {px('radius_md')};
    padding: {px('space_1')}; outline: 0; selection-background-color: {t['accent_soft']};
}}
QComboBox QAbstractItemView::item {{ min-height: {px('button_m')}; padding: 0 {px('space_3')}; }}
QComboBox QAbstractItemView::item:hover {{ background: {t['bg_hover']}; }}
QComboBox QAbstractItemView::item:selected {{ color: {t['accent_hover']}; background: {t['accent_soft']}; border-left: {px('indicator_width')} solid {t['accent']}; }}
QComboBox[rtl="true"] QAbstractItemView::item:selected {{
    border-left: 0; border-right: {px('indicator_width')} solid {t['accent']};
}}
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {{
    subcontrol-origin: border; width: {px('space_5')}; background: transparent; border: 0;
}}
QAbstractSpinBox::up-button {{ subcontrol-position: top right; }}
QAbstractSpinBox::down-button {{ subcontrol-position: bottom right; }}
QAbstractSpinBox[rtl="true"] {{ padding-left: {px('space_6')}; padding-right: {px('input_padding_x')}; }}
QAbstractSpinBox[rtl="true"]::up-button {{ subcontrol-position: top left; }}
QAbstractSpinBox[rtl="true"]::down-button {{ subcontrol-position: bottom left; }}
QAbstractSpinBox::up-button:hover, QAbstractSpinBox::down-button:hover {{ background: {t['ghost_hover']}; }}

QCheckBox, QRadioButton {{ spacing: {px('space_2')}; color: {t['text_primary']}; min-height: {px('button_s')}; }}
QCheckBox::indicator, QRadioButton::indicator {{
    width: {px('checkbox_size')}; height: {px('checkbox_size')};
    border: {px('border_width')} solid {t['border_strong']}; background: {t['bg_layer3']};
}}
QCheckBox::indicator {{ border-radius: {px('radius_sm')}; }}
QRadioButton::indicator {{ border-radius: {px('radius_full')}; }}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {{ border-color: {t['accent']}; }}
QCheckBox::indicator:checked {{ background: {gradient}; border-color: {t['accent']}; }}
QRadioButton::indicator:checked {{ background: {t['accent']}; border: {px('radio_inner_border')} solid {t['accent']}; }}
QCheckBox:focus, QRadioButton:focus {{ outline: none; }}
QCheckBox:focus::indicator, QRadioButton:focus::indicator {{
    border: {px('focus_width')} solid {t['accent_hover']};
}}
QCheckBox:disabled, QRadioButton:disabled {{ color: {t['text_disabled']}; }}

QSlider::groove:horizontal {{ height: {px('slider_track')}; background: {t['bg_layer3']}; border-radius: {px('radius_full')}; }}
QSlider::sub-page:horizontal {{ background: {gradient_horizontal}; border-radius: {px('radius_full')}; }}
QSlider::add-page:horizontal {{ background: {t['bg_layer3']}; border-radius: {px('radius_full')}; }}
QSlider::handle:horizontal {{
    width: {px('slider_knob')}; height: {px('slider_knob')}; margin: {px('slider_handle_margin')} 0;
    background: {t['text_primary']}; border: {px('border_width')} solid {t['border_default']}; border-radius: {px('radius_full')};
}}
QSlider::handle:horizontal:hover {{ background: {t['accent_hover']}; }}
QSlider:focus {{ outline: none; }}
QSlider::handle:horizontal:focus {{ border: {px('focus_width')} solid {t['accent_hover']}; }}

QProgressBar {{
    min-height: {px('progress_height')}; max-height: {px('progress_height')};
    border: 0; border-radius: {px('radius_full')}; background: {t['bg_layer3']};
    color: transparent; text-align: center;
}}
QProgressBar::chunk {{ border-radius: {px('radius_full')}; background: {gradient_horizontal}; }}
QProgressBar[complete="true"]::chunk {{ background: {t['success']}; }}

QScrollArea, QStackedWidget {{ border: 0; background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: {px('scrollbar_width')}; margin: {px('space_1')}; }}
QScrollBar:horizontal {{ background: transparent; height: {px('scrollbar_width')}; margin: {px('space_1')}; }}
QScrollBar::handle:vertical {{ background: {t['border_strong']}; border-radius: {px('radius_full')}; min-height: {px('space_5')}; }}
QScrollBar::handle:horizontal {{ background: {t['border_strong']}; border-radius: {px('radius_full')}; min-width: {px('space_5')}; }}
QScrollBar:vertical:hover {{ width: {px('scrollbar_hover_width')}; }}
QScrollBar:horizontal:hover {{ height: {px('scrollbar_hover_width')}; }}
QScrollBar::handle:hover {{ background: {t['text_tertiary']}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; border: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

QTableWidget, QTreeWidget, QListWidget, QTableView, QTreeView, QListView {{
    background: {t['bg_layer2']}; alternate-background-color: {t['table_alt']};
    color: {t['text_primary']}; border: {px('border_width')} solid {t['border_subtle']};
    border-radius: {px('radius_md')}; gridline-color: {t['border_subtle']};
    selection-background-color: {t['accent_soft']}; selection-color: {t['text_primary']}; outline: 0;
}}
QTableWidget::item, QTreeWidget::item, QListWidget::item {{
    min-height: {px('table_row_height')}; padding: 0 {px('space_2')}; border-bottom: {px('border_width')} solid {t['border_subtle']};
}}
QTableWidget::item:hover, QTreeWidget::item:hover, QListWidget::item:hover {{ background: {t['bg_hover']}; }}
QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {{
    background: {t['accent_soft']}; border-left: {px('indicator_width')} solid {t['accent']};
}}
QTableWidget[rtl="true"]::item:selected, QTreeWidget[rtl="true"]::item:selected,
QListWidget[rtl="true"]::item:selected {{
    border-left: 0; border-right: {px('indicator_width')} solid {t['accent']};
}}
QHeaderView::section {{
    min-height: {px('button_m')}; padding: 0 {px('space_2')};
    background: {t['bg_layer1']}; color: {t['text_tertiary']};
    border: 0; border-bottom: {px('border_width')} solid {t['border_subtle']}; font-size: {px('font_caption')}; font-weight: {t['weight_semibold']};
}}
QTableCornerButton::section {{ background: {t['bg_layer1']}; border: 0; }}

QMenu {{
    background: {t['menu_surface']}; color: {t['text_primary']};
    border: {px('border_width')} solid {t['border_default']}; border-radius: {px('radius_md')}; padding: {px('space_1')};
}}
QMenu::item {{ min-height: {px('button_s')}; padding: 0 {px('space_5')}; border-radius: {px('radius_sm')}; }}
QMenu::item:selected {{ background: {t['bg_hover']}; color: {t['text_primary']}; }}
QMenu::item:disabled {{ color: {t['text_disabled']}; }}
QMenu::separator {{ height: {px('border_width')}; background: {t['border_subtle']}; margin: {px('space_1')} {px('space_2')}; }}
QMenu::icon {{ width: {px('icon_s')}; }}

QDialog, QMessageBox, QFileDialog {{
    background: {t['bg_layer2']}; color: {t['text_primary']};
}}
QDialog#glassDialog {{
    background: {t['glass_surface']}; color: {t['text_primary']};
    border: {px('border_width')} solid {t['border_default']}; border-radius: {px('radius_lg')};
}}
QDialogButtonBox QPushButton {{ min-width: {px('space_7')}; }}
QGroupBox {{
    border: {px('border_width')} solid {t['border_subtle']}; border-radius: {px('radius_md')};
    margin-top: {px('space_4')}; padding: {px('space_4')}; font-weight: {t['weight_semibold']};
}}
QGroupBox::title {{ subcontrol-origin: margin; left: {px('space_3')}; padding: 0 {px('space_1')}; color: {t['text_secondary']}; }}
QTabWidget::pane {{ border: {px('border_width')} solid {t['border_subtle']}; border-radius: {px('radius_md')}; background: {t['bg_layer2']}; }}
QTabBar::tab {{
    min-height: {px('button_m')}; padding: 0 {px('space_4')}; color: {t['text_secondary']};
    border: 0; border-bottom: {px('indicator_height')} solid transparent;
}}
QTabBar::tab:hover {{ color: {t['text_primary']}; }}
QTabBar::tab:selected {{ color: {t['accent_hover']}; border-bottom-color: {t['accent']}; }}
QStatusBar {{ background: {t['bg_layer1']}; color: {t['text_secondary']}; border-top: {px('border_width')} solid {t['border_subtle']}; }}
QToolButton {{ min-width: {px('button_s')}; min-height: {px('button_s')}; border-radius: {px('radius_sm')}; }}
QToolButton:hover {{ background: {t['ghost_hover']}; }}
QWidget#navIndicator {{ background: {gradient_horizontal}; border-radius: {px('radius_full')}; }}
QLabel[navGroup="true"] {{ color: {t['text_tertiary']}; font-weight: {t['weight_semibold']}; }}
QWidget#titleBar {{ background: {t['glass_surface']}; border-bottom: {px('border_width')} solid {t['border_subtle']}; }}
QWidget#toast {{ background: {t['glass_surface']}; border: {px('border_width')} solid {t['border_default']}; border-radius: {px('radius_md')}; }}
QWidget#toast[toastTone="success"] {{ border-left: {px('indicator_width')} solid {t['success']}; }}
QWidget#toast[toastTone="warning"] {{ border-left: {px('indicator_width')} solid {t['warning']}; }}
QWidget#toast[toastTone="danger"] {{ border-left: {px('indicator_width')} solid {t['danger']}; }}
QWidget#toast[toastTone="info"] {{ border-left: {px('indicator_width')} solid {t['info']}; }}
QWidget#toast[rtl="true"] {{ border-left: 0; }}
QWidget#toast[rtl="true"][toastTone="success"] {{ border-right: {px('indicator_width')} solid {t['success']}; }}
QWidget#toast[rtl="true"][toastTone="warning"] {{ border-right: {px('indicator_width')} solid {t['warning']}; }}
QWidget#toast[rtl="true"][toastTone="danger"] {{ border-right: {px('indicator_width')} solid {t['danger']}; }}
QWidget#toast[rtl="true"][toastTone="info"] {{ border-right: {px('indicator_width')} solid {t['info']}; }}
QWidget#dropZone[dragOver="true"] {{ background: {t['accent_soft']}; border: {px('focus_width')} solid {t['accent']}; }}
'''


def _preferred_font(app):
    roots = [asset('fonts')]
    import sys
    if getattr(sys, '_MEIPASS', None):
        roots.insert(0, Path(sys._MEIPASS) / 'assets' / 'fonts')
    loaded = set()
    for root in roots:
        for path in root.glob('*.ttf'):
            if path.name.startswith('Vazirmatn') and str(path) not in loaded:
                QFontDatabase.addApplicationFont(str(path))
                loaded.add(str(path))
    font = QFont()
    font.setFamilies(['Inter', 'Segoe UI Variable', 'Segoe UI', 'Vazirmatn', 'DejaVu Sans'])
    font.setPointSize(int(token('font_body')))
    font.setWeight(QFont.Weight.Normal)
    font.setHintingPreference(QFont.HintingPreference.PreferDefaultHinting)
    app.setFont(font)


def apply_theme(app, mode='system'):
    """Apply dark/light/system styling and refresh custom-painted widgets."""
    selected = resolve_theme(mode, app)
    set_active_theme(selected)
    set_reduce_motion(windows_reduce_motion())
    _preferred_font(app)
    app.setStyle('Fusion')
    app.setStyleSheet(build_qss(tokens(selected)))
    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor(token('bg_base')))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(token('text_primary')))
    palette.setColor(QPalette.ColorRole.Base, QColor(token('bg_layer3')))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(token('table_alt')))
    palette.setColor(QPalette.ColorRole.Text, QColor(token('text_primary')))
    palette.setColor(QPalette.ColorRole.Button, QColor(token('bg_layer3')))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(token('text_primary')))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(token('accent')))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(token('text_on_accent')))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(token('text_tertiary')))
    app.setPalette(palette)
    app.setProperty('themeMode', mode)

    # Repaint custom QPainter widgets after switching the shared token palette.
    for widget in app.allWidgets():
        widget.update()
        refresh = getattr(widget, 'refresh_icon', None)
        if callable(refresh):
            refresh()

    # Respect live Windows/desktop theme changes when the preference is System.
    hints = app.styleHints()
    if not getattr(app, '_obsidian_theme_watcher', False):
        changed = getattr(hints, 'colorSchemeChanged', None)
        if changed is not None:
            changed.connect(lambda *_: apply_theme(app, 'system')
                            if app.property('themeMode') == 'system' else None)
        app._obsidian_theme_watcher = True
    return selected


# Kept as a convenience for callers that inspect the default stylesheet.
QSS = build_qss(tokens('dark'))
