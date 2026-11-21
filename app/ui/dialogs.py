from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import QFileDialog, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QApplication
from app.ui.design_tokens import token
from app.i18n import tr
from .widgets.common import GlassDialog, button


def folder(parent, initial=''):
    return QFileDialog.getExistingDirectory(parent, tr('Select folder'), initial,
                                             QFileDialog.Option.DontUseNativeDialog)


def save_file(parent, name, filters):
    return QFileDialog.getSaveFileName(parent, tr('Export'), name, filters,
                                       options=QFileDialog.Option.DontUseNativeDialog)[0]


def details(parent, title, text):
    dialog = GlassDialog(parent)
    dialog.setWindowTitle(title)
    dialog.resize(int(token('details_dialog_width')), int(token('details_dialog_height')))
    box = QVBoxLayout(dialog)
    box.setContentsMargins(token('space_5'), token('space_5'), token('space_5'), token('space_5'))
    box.setSpacing(token('space_3'))
    edit = QPlainTextEdit(text)
    edit.setReadOnly(True)
    font = edit.font()
    font.setFamilies(['JetBrains Mono', 'Cascadia Code', 'Cascadia Mono', 'Consolas', 'DejaVu Sans Mono'])
    font.setPointSize(int(token('font_caption')))
    edit.setFont(font)
    box.addWidget(edit, 1)
    actions = QHBoxLayout()
    actions.setSpacing(token('space_2'))
    actions.addStretch()
    actions.addWidget(button('Copy', lambda: QApplication.clipboard().setText(text), variant='secondary'))
    actions.addWidget(button('Close', dialog.accept, primary=True))
    box.addLayout(actions)
    dialog.exec()


def open_folder(path):
    from pathlib import Path
    target = Path(path)
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(target if target.is_dir() else target.parent)))
