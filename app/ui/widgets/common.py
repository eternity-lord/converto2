"""Shared Obsidian Glass controls and custom-painted Qt primitives.

Application pages use these controls so visual states, accessibility, RTL behavior,
and palette changes stay consistent without touching processing logic.
"""
from collections import deque

from PySide6.QtCore import (
    Qt, Signal, Property, QPropertyAnimation, QEasingCurve, QRectF, QPointF,
    QSize, QTimer, QParallelAnimationGroup, QEvent,
)
from PySide6.QtGui import (
    QColor, QPainter, QPainterPath, QLinearGradient, QRadialGradient, QPen,
    QPixmap, QIcon, QStyleOptionButton, QPalette, QTransform,
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QScrollArea, QSizeGrip, QSizePolicy,
    QProgressBar, QTableWidget, QDialog, QGraphicsOpacityEffect, QStyle,
    QFrame, QCheckBox,
)
from app.i18n import tr
from app.ui.design_tokens import duration, elevation, motion_easing, reduce_motion, token


def _qcolor(value):
    """Convert a shared hex/named/CSS-rgba token to QColor without alpha loss."""
    if isinstance(value, QColor):
        return QColor(value)
    if isinstance(value, str) and value.strip().lower().startswith('rgba('):
        try:
            channels = [float(part.strip()) for part in value[value.index('(') + 1:value.rindex(')')].split(',')]
            if len(channels) == 4:
                alpha = channels[3] * 255 if 0.0 <= channels[3] <= 1.0 else channels[3]
                values = [max(0, min(255, round(channel))) for channel in (*channels[:3], alpha)]
                return QColor(*values)
        except (ValueError, IndexError):
            pass
    return QColor(value)


def _curve(name='standard'):
    x1, y1, x2, y2 = motion_easing(name)
    curve = QEasingCurve(QEasingCurve.Type.BezierSpline)
    curve.addCubicBezierSegment(QPointF(x1, y1), QPointF(x2, y2), QPointF(1.0, 1.0))
    return curve


def label(text, role=None):
    widget = QLabel(tr(text))
    widget.setWordWrap(True)
    if role:
        widget.setProperty('role', role)
    if role == 'mono':
        font = widget.font()
        font.setFamilies(['JetBrains Mono', 'Cascadia Code', 'Cascadia Mono', 'Consolas', 'DejaVu Sans Mono'])
        widget.setFont(font)
    return widget


def icon(name, color=None, size=None, mirror=False):
    """Return a crisp 1.5px line icon from one small platform-neutral set."""
    size = int(size or token('icon_m'))
    color = color or token('text_secondary')
    scale = size / float(token('icon_grid'))
    pixmap = QPixmap(size * 2, size * 2)
    pixmap.fill(Qt.GlobalColor.transparent)
    pixmap.setDevicePixelRatio(2)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    p.scale(scale, scale)
    pen = QPen(_qcolor(color), float(token('icon_stroke')))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    if name == 'dashboard':
        for x, y in ((2.5, 2.5), (10, 2.5), (2.5, 10), (10, 10)):
            p.drawRoundedRect(QRectF(x, y, 5.5, 5.5), 1.6, 1.6)
    elif name == 'fixer':
        for y, knob in ((5, 6), (9, 12), (13, 8)):
            p.drawLine(QPointF(2, y), QPointF(16, y))
            p.setBrush(_qcolor(token('bg_layer2')))
            p.drawEllipse(QPointF(knob, y), 2.1, 2.1)
            p.setBrush(Qt.BrushStyle.NoBrush)
    elif name == 'hqx':
        for y in (4, 9, 14):
            path = QPainterPath(QPointF(3, y + 1.5))
            path.lineTo(9, y - 2)
            path.lineTo(15, y + 1.5)
            p.drawPath(path)
    elif name == 'qsv':
        p.drawRoundedRect(QRectF(4.5, 4.5, 9, 9), 2, 2)
        p.drawRoundedRect(QRectF(7.5, 7.5, 3, 3), .8, .8)
        for offset in (6.5, 9, 11.5):
            p.drawLine(QPointF(offset, 1.5), QPointF(offset, 4.2))
            p.drawLine(QPointF(offset, 13.8), QPointF(offset, 16.5))
            p.drawLine(QPointF(1.5, offset), QPointF(4.2, offset))
            p.drawLine(QPointF(13.8, offset), QPointF(16.5, offset))
    elif name == 'tweaks':
        p.drawLine(QPointF(6, 2.5), QPointF(6, 15.5))
        p.drawLine(QPointF(12, 2.5), QPointF(12, 15.5))
        p.setBrush(_qcolor(token('bg_layer2')))
        p.drawEllipse(QPointF(6, 11), 2.2, 2.2)
        p.drawEllipse(QPointF(12, 6), 2.2, 2.2)
    elif name == 'logs':
        p.drawRoundedRect(QRectF(3.5, 2.5, 11, 13), 2, 2)
        for y in (6, 9, 12):
            p.drawLine(QPointF(6, y), QPointF(12, y))
    elif name == 'settings':
        p.drawEllipse(QPointF(9, 9), 5.4, 5.4)
        p.drawEllipse(QPointF(9, 9), 2.2, 2.2)
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0),
                       (-.71, -.71), (.71, -.71), (-.71, .71), (.71, .71)):
            p.drawLine(QPointF(9 + dx * 5.4, 9 + dy * 5.4), QPointF(9 + dx * 7.1, 9 + dy * 7.1))
    elif name == 'support':
        p.drawEllipse(QPointF(9, 9), 6.4, 6.4)
        p.drawEllipse(QPointF(9, 9), 2.4, 2.4)
        for dx, dy in ((-4.5, -4.5), (4.5, -4.5), (-4.5, 4.5), (4.5, 4.5)):
            p.drawLine(QPointF(9 + dx * .55, 9 + dy * .55), QPointF(9 + dx, 9 + dy))
    elif name == 'bell':
        path = QPainterPath(QPointF(4.5, 12.5))
        path.lineTo(4.5, 8.5)
        path.arcTo(QRectF(4.5, 3, 9, 9), 180, -180)
        path.lineTo(13.5, 12.5)
        path.closeSubpath()
        p.drawPath(path)
        p.drawLine(QPointF(7.5, 14.5), QPointF(10.5, 14.5))
    elif name == 'queue':
        for y in (4.5, 9, 13.5):
            p.drawLine(QPointF(2.5, y), QPointF(12.5, y))
        path = QPainterPath(QPointF(14, 6.5))
        path.lineTo(17, 9)
        path.lineTo(14, 11.5)
        path.closeSubpath()
        p.drawPath(path)
    elif name == 'monitor':
        p.drawRoundedRect(QRectF(2, 3, 14, 9.5), 1.8, 1.8)
        p.drawLine(QPointF(6.5, 15), QPointF(11.5, 15))
        p.drawLine(QPointF(9, 12.5), QPointF(9, 15))
    elif name == 'search':
        p.drawEllipse(QPointF(8, 8), 4.6, 4.6)
        p.drawLine(QPointF(11.4, 11.4), QPointF(15.5, 15.5))
    elif name == 'minimize':
        p.drawLine(QPointF(4, 12), QPointF(14, 12))
    elif name == 'maximize':
        p.drawRoundedRect(QRectF(4, 4, 10, 10), 1.2, 1.2)
    elif name == 'close':
        p.drawLine(QPointF(5, 5), QPointF(13, 13))
        p.drawLine(QPointF(13, 5), QPointF(5, 13))
    elif name in ('collapse', 'expand'):
        p.drawRoundedRect(QRectF(2.5, 3, 13, 12), 1.5, 1.5)
        p.drawLine(QPointF(6, 3.5), QPointF(6, 14.5))
        if name == 'collapse':
            p.drawLine(QPointF(11.5, 7), QPointF(9.5, 9))
            p.drawLine(QPointF(9.5, 9), QPointF(11.5, 11))
        else:
            p.drawLine(QPointF(8.5, 7), QPointF(10.5, 9))
            p.drawLine(QPointF(10.5, 9), QPointF(8.5, 11))
    elif name == 'chevron':
        path = QPainterPath(QPointF(6, 4.5))
        path.lineTo(11, 9)
        path.lineTo(6, 13.5)
        p.drawPath(path)
    elif name == 'brand':
        shape = QPainterPath()
        shape.addRoundedRect(QRectF(1, 1, 16, 16), 4, 4)
        fill = QLinearGradient(QPointF(1, 1), QPointF(17, 17))
        fill.setColorAt(0, _qcolor(token('accent_gradient_start')))
        fill.setColorAt(1, _qcolor(token('accent_gradient_end')))
        p.fillPath(shape, fill)
        pen = QPen(_qcolor(token('text_on_accent')), float(token('icon_stroke')))
        pen.setCapStyle(Qt.PenCapStyle.SquareCap)
        p.setPen(pen)
        p.drawLine(QPointF(6, 4), QPointF(6, 14))
        p.drawLine(QPointF(12, 4), QPointF(12, 14))
        p.drawLine(QPointF(6, 9), QPointF(12, 9))
    p.end()
    if mirror:
        pixmap = pixmap.transformed(QTransform().scale(-1, 1))
    return QIcon(pixmap)


class DesignButton(QPushButton):
    """Keyboard-friendly button with lightweight hover/press/ripple feedback."""

    def __init__(self, text='', callback=None, variant='secondary', glyph=None, size='M'):
        super().__init__(text)
        self.setProperty('variant', variant)
        self.setProperty('buttonSize', str(size).upper())
        self.setProperty('primary', variant == 'primary')
        self.setProperty('iconOnly', not bool(text) and bool(glyph))
        self.setProperty('iconGlyph', glyph or '')
        self._glyph = glyph
        self._hover_value = 0.0
        self._press_value = 0.0
        self._ripple_value = 1.0
        self._ripple_center = QPointF()
        self._loading = False
        self._loading_angle = 0
        self._spinner_timer = QTimer(self)
        self._spinner_timer.setInterval(int(token('frame_interval')))
        self._spinner_timer.timeout.connect(self._advance_spinner)
        self._hover_anim = QPropertyAnimation(self, b'hoverProgress', self)
        self._press_anim = QPropertyAnimation(self, b'pressProgress', self)
        self._ripple_anim = QPropertyAnimation(self, b'rippleProgress', self)
        self._ripple_anim.setDuration(duration('ripple'))
        self._ripple_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTipDuration(int(token('tooltip_delay')))
        if glyph:
            self.setIconSize(QSize(int(token('button_icon')), int(token('button_icon'))))
            self.refresh_icon()
        if variant == 'primary':
            effect = QGraphicsDropShadowEffect(self)
            shadow_color, blur, y = elevation('e1')
            effect.setColor(_qcolor(shadow_color))
            effect.setBlurRadius(blur)
            effect.setOffset(0, y)
            self.setGraphicsEffect(effect)
            self._shadow = effect
        else:
            self._shadow = None
        if callback is not None:
            self.clicked.connect(callback)

    def refresh_icon(self):
        glyph = getattr(self, '_glyph', None)
        if not glyph:
            return
        if self.property('variant') == 'primary':
            color = token('text_on_accent')
        elif self.property('nav') and self.isChecked():
            color = token('icon_active')
        elif self.underMouse():
            color = token('text_primary')
        else:
            color = token('text_secondary')
        mirror = (self.layoutDirection() == Qt.LayoutDirection.RightToLeft and
                  glyph in {'queue', 'chevron', 'collapse', 'expand'})
        self.setIcon(icon(glyph, color, int(token('icon_m')), mirror=mirror))

    def _animate(self, animation, property_name, start, end, motion='fast'):
        animation.stop()
        if reduce_motion():
            self.setProperty(property_name.decode() if isinstance(property_name, bytes) else property_name, end)
            return
        animation.setTargetObject(self)
        animation.setPropertyName(property_name)
        animation.setDuration(duration(motion))
        animation.setEasingCurve(_curve('standard'))
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.start()

    def enterEvent(self, event):
        self._animate(self._hover_anim, b'hoverProgress', self._hover_value, 1.0, 'fast')
        self.refresh_icon()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate(self._hover_anim, b'hoverProgress', self._hover_value, 0.0, 'fast')
        self.refresh_icon()
        super().leaveEvent(event)

    def setLoading(self, loading):
        loading = bool(loading)
        if self._loading == loading:
            return
        self._loading = loading
        self.setProperty('loading', loading)
        self.setAccessibleDescription(tr('Loading') if loading else '')
        self.setCursor(Qt.CursorShape.WaitCursor if loading else Qt.CursorShape.PointingHandCursor)
        if loading and not reduce_motion():
            self._spinner_timer.start()
        else:
            self._spinner_timer.stop()
        self.update()

    def _advance_spinner(self):
        self._loading_angle = (self._loading_angle + int(token('loading_spinner_step'))) % 360
        self.update()

    def keyPressEvent(self, event):
        if self._loading:
            event.ignore()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if self._loading:
            event.ignore()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._ripple_center = event.position()
            self._animate(self._press_anim, b'pressProgress', self._press_value, 1.0, 'instant')
            if self.property('variant') == 'primary' and not reduce_motion():
                self._ripple_value = 0.0
                self._ripple_anim.stop()
                self._ripple_anim.setStartValue(0.0)
                self._ripple_anim.setEndValue(1.0)
                self._ripple_anim.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self._loading:
            event.ignore()
            return
        super().mouseReleaseEvent(event)
        self._animate(self._press_anim, b'pressProgress', self._press_value, 0.0, 'instant')
        self.refresh_icon()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.Type.StyleChange, QEvent.Type.PaletteChange,
                            QEvent.Type.EnabledChange, QEvent.Type.LayoutDirectionChange):
            self.refresh_icon()
            if self.isEnabled():
                self.setCursor(Qt.CursorShape.WaitCursor if self._loading else Qt.CursorShape.PointingHandCursor)
            else:
                self.setCursor(Qt.CursorShape.ForbiddenCursor)

    def getHoverProgress(self):
        return self._hover_value

    def setHoverProgress(self, value):
        self._hover_value = float(value)
        if self._shadow is not None:
            _, blur, y = elevation('e1')
            self._shadow.setBlurRadius(blur + float(token('shadow_e2_blur') - blur) * self._hover_value)
            self._shadow.setOffset(0, y + float(token('space_1')) * self._hover_value)
            self._shadow.setColor(_qcolor(token('accent_glow')) if self._hover_value else _qcolor(token('shadow_e1')))
        self.update()

    hoverProgress = Property(float, getHoverProgress, setHoverProgress)

    def getPressProgress(self):
        return self._press_value

    def setPressProgress(self, value):
        self._press_value = float(value)
        self.update()

    pressProgress = Property(float, getPressProgress, setPressProgress)

    def getRippleProgress(self):
        return self._ripple_value

    def setRippleProgress(self, value):
        self._ripple_value = float(value)
        self.update()

    rippleProgress = Property(float, getRippleProgress, setRippleProgress)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        hover = self._hover_value
        press = self._press_value
        scale = 1.0 + (float(token('button_hover_scale')) * hover) - (float(token('button_press_scale')) * press)
        lift = float(token('button_hover_lift')) * hover
        painter.translate((self.width() * (1 - scale)) / 2,
                          (self.height() * (1 - scale)) / 2 - lift)
        painter.scale(scale, scale)
        option = QStyleOptionButton()
        self.initStyleOption(option)
        if self._loading:
            option.text = ''
            option.icon = QIcon()
        self.style().drawControl(QStyle.ControlElement.CE_PushButton, option, painter, self)
        if self._loading:
            side = float(token('loading_spinner_size'))
            rect = QRectF((self.width() - side) / 2, (self.height() - side) / 2, side, side)
            spinner_color = token('text_on_accent') if self.property('variant') == 'primary' else token('accent_hover')
            pen = QPen(_qcolor(spinner_color), float(token('loading_spinner_stroke')))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            units = int(token('qt_angle_units'))
            painter.drawArc(rect, self._loading_angle * units, int(token('loading_spinner_arc') * units))
        if self._ripple_value < 1.0 and self.property('variant') == 'primary':
            path = QPainterPath()
            path.addRoundedRect(QRectF(0, 0, self.width(), self.height()),
                                float(token('radius_sm')), float(token('radius_sm')))
            painter.setClipPath(path)
            color = _qcolor(token('ripple'))
            color.setAlphaF(color.alphaF() * max(0.0, 1.0 - self._ripple_value))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            radius = max(self.width(), self.height()) * self._ripple_value
            painter.drawEllipse(self._ripple_center, radius, radius)
        painter.end()


def button(text, callback=None, primary=False, glyph=None, variant=None, size='M'):
    text = tr(text).replace('&', '&&')
    selected_variant = variant or ('primary' if primary else 'secondary')
    return DesignButton(text, callback, selected_variant, glyph, size)


def row(*widgets):
    layout = QHBoxLayout()
    layout.setContentsMargins(token('space_0'), token('space_0'), token('space_0'), token('space_0'))
    layout.setSpacing(int(token('space_2')))
    for widget in widgets:
        if isinstance(widget, QWidget):
            layout.addWidget(widget)
        else:
            layout.addStretch()
    return layout


class Card(QWidget):
    def __init__(self, title='', glow=False, surface='card', interactive=False):
        super().__init__()
        self.glow = glow
        self.surface = surface
        self.interactive = interactive
        self.setProperty('surface', surface)
        self.setProperty('interactive', interactive)
        self.box = QVBoxLayout(self)
        pad = int(token('card_padding'))
        self.box.setContentsMargins(pad, pad, pad, pad)
        self.box.setSpacing(int(token('card_spacing')))
        if title:
            self.box.addWidget(label(title, 'subtitle'))
        if interactive:
            effect = QGraphicsDropShadowEffect(self)
            color, blur, y = elevation('e1')
            effect.setColor(_qcolor(color))
            effect.setBlurRadius(blur)
            effect.setOffset(0, y)
            self.setGraphicsEffect(effect)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        inset = float(token('border_inset'))
        rect = QRectF(self.rect()).adjusted(inset, inset, -inset, -inset)
        radius = float(token('radius_lg')) if self.surface == 'glass' else float(token('radius_md'))
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        fill = _qcolor(token('glass_surface' if self.surface == 'glass' else 'bg_layer2'))
        painter.fillPath(path, fill)
        if self.glow:
            gradient = QRadialGradient(QPointF(self.width() * .78, self.height() * .08),
                                       max(self.width(), self.height()) * .82)
            glow = _qcolor(token('card_glow'))
            gradient.setColorAt(0, glow)
            gradient.setColorAt(1, QColor(glow.red(), glow.green(), glow.blue(), 0))
            painter.fillPath(path, gradient)
        painter.setPen(QPen(_qcolor(token('glass_border' if self.surface == 'glass' else 'border_subtle')),
                            float(token('border_width'))))
        painter.drawPath(path)
        painter.setPen(QPen(_qcolor(token('inner_highlight')), float(token('border_width'))))
        highlight_offset = float(token('border_width'))
        painter.drawLine(QPointF(rect.left() + radius, rect.top() + highlight_offset),
                         QPointF(rect.right() - radius, rect.top() + highlight_offset))
        painter.end()


class Toggle(QCheckBox):
    """Native accessible checkbox semantics, painted as an animated switch."""

    def __init__(self, text='', checked=False, compact=False):
        super().__init__('')
        self._position = float(bool(checked))
        self._pressed = False
        self.animation = QPropertyAnimation(self, b'position', self)
        self.animation.setDuration(duration('base'))
        self.animation.setEasingCurve(_curve('spring'))
        self.setText(text)
        self.setChecked(bool(checked))
        self.setMinimumHeight(max(int(token('button_s')), int(token('toggle_height'))))
        self.setMinimumWidth(int(token('toggle_width')))
        self.setSizePolicy(QSizePolicy.Policy.Fixed if compact else QSizePolicy.Policy.Preferred,
                           QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleDescription(tr('On') if checked else tr('Off'))
        self.setToolTipDuration(int(token('tooltip_delay')))
        self.toggled.connect(self._checked_changed)
        self.pressed.connect(self._set_pressed)
        self.released.connect(self._clear_pressed)

    def setText(self, text):
        translated = tr(text)
        super().setText(translated.replace('&', '&&'))
        self.setAccessibleName(translated)
        if hasattr(self, '_position'):
            self.updateGeometry()
            self.update()

    def sizeHint(self):
        text = self.text().replace('&&', '&')
        width = self.fontMetrics().horizontalAdvance(text)
        width += int(token('toggle_width')) + int(token('space_2'))
        height = max(int(token('button_s')), int(token('toggle_height')))
        return QSize(width, height)

    def _checked_changed(self, checked):
        self.setAccessibleDescription(tr('On') if checked else tr('Off'))
        self.animation.stop()
        if reduce_motion():
            self._position = float(checked)
            self.update()
        else:
            self.animation.setDuration(duration('base'))
            self.animation.setEasingCurve(_curve('spring'))
            self.animation.setStartValue(self._position)
            self.animation.setEndValue(float(checked))
            self.animation.start()

    def _set_pressed(self):
        self._pressed = True
        self.update()

    def _clear_pressed(self):
        self._pressed = False
        self.update()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.click()
            event.accept()
            return
        super().keyPressEvent(event)

    def getPosition(self):
        return self._position

    def setPosition(self, value):
        self._position = float(value)
        self.update()

    position = Property(float, getPosition, setPosition)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width, height = float(token('toggle_width')), float(token('toggle_height'))
        inset = float(token('space_1'))
        rtl = self.layoutDirection() == Qt.LayoutDirection.RightToLeft
        x = inset if rtl else self.width() - width - inset
        y = (self.height() - height) / 2
        track = QRectF(x, y, width, height)
        focus = self.hasFocus()
        border = token('accent') if self.isChecked() or focus else token('border_default')
        border_width = float(token('focus_width') if focus else token('border_width'))
        painter.setPen(QPen(_qcolor(border), border_width))
        if self.isChecked():
            fill = QLinearGradient(track.topLeft(), track.topRight())
            fill.setColorAt(0, _qcolor(token('accent_gradient_start')))
            fill.setColorAt(1, _qcolor(token('accent_gradient_end')))
            painter.setBrush(fill)
        else:
            painter.setBrush(_qcolor(token('bg_layer3' if self.isEnabled() else 'bg_layer2')))
        painter.drawRoundedRect(track, height / 2, height / 2)

        knob_size = float(token('toggle_knob'))
        travel = width - knob_size - inset * 2
        if rtl:
            knob_x = x + inset + travel * (1.0 - self._position)
        else:
            knob_x = x + inset + travel * self._position
        if self._pressed:
            knob_size += float(token('space_1'))
        painter.setPen(Qt.PenStyle.NoPen)
        knob_color = token('text_on_accent') if self.isChecked() else token('text_tertiary')
        if not self.isEnabled():
            knob_color = token('text_disabled')
        painter.setBrush(_qcolor(knob_color))
        painter.drawEllipse(QRectF(knob_x, y + (height - float(token('toggle_knob'))) / 2,
                                   knob_size, float(token('toggle_knob'))))

        gap = float(token('space_1'))
        if rtl:
            text_rect = QRectF(x + width + gap, 0, max(0, self.width() - x - width - gap), self.height())
            alignment = Qt.AlignmentFlag.AlignRight
            elide = Qt.TextElideMode.ElideLeft
        else:
            text_rect = QRectF(0, 0, max(0, x - gap), self.height())
            alignment = Qt.AlignmentFlag.AlignLeft
            elide = Qt.TextElideMode.ElideRight
        display_text = self.fontMetrics().elidedText(self.text().replace('&&', '&'), elide,
                                                     max(0, int(text_rect.width())))
        painter.setFont(self.font())
        self.style().drawItemText(painter, text_rect.toRect(),
                                  alignment | Qt.AlignmentFlag.AlignVCenter,
                                  self.palette(), self.isEnabled(), display_text,
                                  QPalette.ColorRole.ButtonText)
        painter.end()


class Pills(QWidget):
    selected = Signal(str)

    def __init__(self, values, selected=None):
        super().__init__()
        self.value = selected or values[0]
        self.buttons = {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(token('space_0'), token('space_0'), token('space_0'), token('space_0'))
        layout.setSpacing(int(token('space_1')))
        for value in values:
            btn = button(value, variant='segmented')
            btn.setCheckable(True)
            btn.setChecked(value == self.value)
            btn.setAccessibleName(tr(value))
            btn.clicked.connect(lambda checked=False, v=value: self.choose(v))
            layout.addWidget(btn)
            self.buttons[value] = btn
        layout.addStretch()

    def choose(self, value):
        self.value = value
        for key, btn in self.buttons.items():
            btn.setChecked(key == value)
            btn.refresh_icon()
        self.selected.emit(value)


class Chart(QWidget):
    def __init__(self, capacity=180):
        super().__init__()
        self.values = deque(maxlen=capacity)
        self.setMinimumHeight(int(token('chart_min_height')))
        self.setAccessibleName(tr('Encoding performance chart'))

    def append(self, value):
        self.values.append(float(value))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        rect = QRectF(token('chart_left_padding'), token('chart_top_padding'),
                      max(1, self.width() - token('chart_left_padding') - token('chart_right_padding')),
                      max(1, self.height() - token('chart_top_padding') - token('chart_bottom_padding')))
        vals = list(self.values)
        maximum = max(1, max(vals, default=1)) * float(token('chart_headroom'))
        grid_color = _qcolor(token('grid'))
        grid_count = int(token('chart_grid_lines'))
        grid_denominator = max(1, grid_count - 1)
        p.setPen(QPen(grid_color, float(token('border_width'))))
        for i in range(grid_count):
            y = rect.top() + rect.height() * i / grid_denominator
            p.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
            p.setPen(_qcolor(token('text_tertiary')))
            p.drawText(QRectF(0, y - token('space_1'), token('chart_left_padding') - token('space_1'),
                              token('space_3')), Qt.AlignmentFlag.AlignRight,
                       f'{maximum * (1 - i / grid_denominator):.1f}')
            p.setPen(QPen(grid_color, float(token('border_width'))))
        if len(vals) < 2:
            p.setPen(_qcolor(token('text_tertiary')))
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, tr('Ready') + ' · ' + tr('live telemetry'))
            return
        points = [QPointF(rect.left() + i / (len(vals) - 1) * rect.width(),
                          rect.bottom() - v / maximum * rect.height()) for i, v in enumerate(vals)]
        line = QPainterPath(points[0])
        for point in points[1:]:
            line.lineTo(point)
        area = QPainterPath(line)
        area.lineTo(rect.bottomRight())
        area.lineTo(rect.bottomLeft())
        area.closeSubpath()
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0, _qcolor(token('chart_fill')))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        p.fillPath(area, gradient)
        p.setPen(QPen(_qcolor(token('chart_line')), float(token('icon_stroke'))))
        p.drawPath(line)
        point = points[-1]
        p.setPen(QPen(_qcolor(token('accent_glow')), float(token('border_width')), Qt.PenStyle.DashLine))
        p.drawLine(point, QPointF(point.x(), rect.bottom()))
        glow_color = _qcolor(token('accent_glow'))
        glow_color.setAlphaF(float(token('chart_glow_opacity')))
        glow = QRadialGradient(point, float(token('space_5')))
        glow.setColorAt(0, _qcolor(token('accent_hover')))
        glow.setColorAt(1, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(glow)
        p.drawEllipse(point, float(token('space_5')), float(token('space_5')))
        p.setBrush(_qcolor(token('accent_hover')))
        p.drawEllipse(point, float(token('space_1')) / 2, float(token('space_1')) / 2)
        p.setPen(_qcolor(token('text_secondary')))
        p.drawText(QRectF(rect.left(), rect.bottom() + token('space_2'), rect.width(), token('space_4')),
                   Qt.AlignmentFlag.AlignLeft, tr('Earlier'))
        p.drawText(QRectF(rect.left(), rect.bottom() + token('space_2'), rect.width(), token('space_4')),
                   Qt.AlignmentFlag.AlignRight, f'{vals[-1]:.2f}  {tr("now")}')


class ProgressBar(QProgressBar):
    """Token-styled progress bar with a lightweight, visibility-aware shimmer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(int(token('frame_interval')))
        self._timer.timeout.connect(self._advance)
        self.valueChanged.connect(self._sync_state)
        self._sync_state(self.value())

    def _sync_state(self, value):
        self.setProperty('complete', self.maximum() > self.minimum() and value >= self.maximum())
        if self.isVisible() and not reduce_motion() and (self.maximum() == self.minimum() or value < self.maximum()):
            if not self._timer.isActive():
                self._timer.start()
        else:
            self._timer.stop()
        self.update()

    def _advance(self):
        self._phase = (self._phase + float(token('shimmer_step'))) % 1.0
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        self._sync_state(self.value())

    def hideEvent(self, event):
        self._timer.stop()
        super().hideEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if reduce_motion() or (self.maximum() > self.minimum() and self.value() >= self.maximum()):
            return
        if self.maximum() == self.minimum():
            chunk_width = self.width() * float(token('progress_shimmer_indeterminate'))
            x = (self.width() + chunk_width) * self._phase - chunk_width
        else:
            chunk_width = self.width() * (self.value() - self.minimum()) / max(1, self.maximum() - self.minimum())
            x = max(0.0, chunk_width * self._phase - chunk_width * float(token('progress_shimmer_offset')))
            chunk_width = min(self.width() - x, max(0.0, chunk_width * float(token('progress_shimmer_width'))))
        if chunk_width <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setClipRect(QRectF(0, 0, self.width(), self.height()))
        light = QLinearGradient(QPointF(x, 0), QPointF(x + chunk_width, 0))
        clear = _qcolor(token('shimmer'))
        clear.setAlpha(0)
        light.setColorAt(0, clear)
        light.setColorAt(.5, _qcolor(token('shimmer')))
        light.setColorAt(1, clear)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(light)
        painter.drawRoundedRect(QRectF(x, 0, chunk_width, self.height()),
                                float(token('radius_full')), float(token('radius_full')))
        painter.end()


class ProgressRing(QWidget):
    """Reusable accessible circular progress indicator with monospaced percentage."""

    def __init__(self, value=0, parent=None):
        super().__init__(parent)
        self._value = max(0, min(100, int(value)))
        self.setMinimumSize(int(token('space_7')), int(token('space_7')))
        self.setAccessibleName(f'{self._value}%')

    def setValue(self, value):
        self._value = max(0, min(100, int(value)))
        self.setAccessibleName(f'{self._value}%')
        self.update()

    def value(self):
        return self._value

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = min(self.width(), self.height())
        width = float(token('icon_stroke')) * 2 + float(token('border_width'))
        rect = QRectF((self.width() - side) / 2 + width,
                      (self.height() - side) / 2 + width,
                      side - width * 2, side - width * 2)
        units = int(token('qt_angle_units'))
        painter.setPen(QPen(_qcolor(token('bg_layer3')), width))
        painter.drawArc(rect, 0, 360 * units)
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0, _qcolor(token('accent_gradient_start')))
        gradient.setColorAt(1, _qcolor(token('accent_gradient_end')))
        pen = QPen(gradient, width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 90 * units, -int(360 * units * self._value / 100))
        painter.setPen(_qcolor(token('text_primary')))
        font = painter.font()
        font.setFamilies(['JetBrains Mono', 'Cascadia Code', 'Consolas', 'DejaVu Sans Mono'])
        font.setPointSize(int(token('font_caption')))
        painter.setFont(font)
        painter.drawText(QRectF(0, 0, self.width(), self.height()), Qt.AlignmentFlag.AlignCenter,
                         f'{self._value}%')
        painter.end()


class Skeleton(QWidget):
    """Small shimmer placeholder for lazy page/list loading; pauses when hidden."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._phase = 0.0
        self.setMinimumHeight(int(token('button_m')))
        self._timer = QTimer(self)
        self._timer.setInterval(int(token('frame_interval')))
        self._timer.timeout.connect(self._advance)

    def _advance(self):
        self._phase = (self._phase + float(token('shimmer_step'))) % 1.0
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        if not reduce_motion():
            self._timer.start()

    def hideEvent(self, event):
        self._timer.stop()
        super().hideEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0, 0, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, float(token('radius_sm')), float(token('radius_sm')))
        painter.fillPath(path, _qcolor(token('bg_layer3')))
        if not reduce_motion():
            band = rect.width() * float(token('skeleton_shimmer_width'))
            start = rect.left() + (rect.width() + band) * self._phase - band
            gradient = QLinearGradient(QPointF(start, 0), QPointF(start + band, 0))
            clear = _qcolor(token('shimmer'))
            clear.setAlpha(0)
            gradient.setColorAt(0, clear)
            gradient.setColorAt(.5, _qcolor(token('shimmer')))
            gradient.setColorAt(1, clear)
            painter.fillPath(path, gradient)
        painter.end()


class EmptyTable(QTableWidget):
    """Table with a quiet branded empty state instead of a blank dark rectangle."""

    def __init__(self, rows=0, columns=1, parent=None, empty_title='Nothing here yet', empty_body=''):
        super().__init__(rows, columns, parent)
        self.empty_title = tr(empty_title)
        self.empty_body = tr(empty_body)
        self.setAlternatingRowColors(True)

    def setEmptyState(self, title, body=''):
        self.empty_title = tr(title)
        self.empty_body = tr(body)
        self.viewport().update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.rowCount() != 0:
            return
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bounds = self.viewport().rect()
        center = QPointF(bounds.center().x(), bounds.center().y() - token('space_3'))
        painter.setPen(QPen(_qcolor(token('accent_glow')), float(token('border_width'))))
        painter.setBrush(_qcolor(token('accent_soft')))
        icon_size = float(token('space_7'))
        painter.drawEllipse(QRectF(center.x() - icon_size / 2, center.y() - icon_size / 2,
                                   icon_size, icon_size))
        painter.setPen(QPen(_qcolor(token('accent_hover')), float(token('icon_stroke'))))
        painter.drawRoundedRect(QRectF(center.x() - token('space_3'), center.y() - token('space_3'),
                                       token('space_6'), token('space_6')),
                               float(token('radius_sm')), float(token('radius_sm')))
        title_rect = QRectF(0, center.y() + token('space_7') / 2,
                            bounds.width(), token('space_5'))
        painter.setPen(_qcolor(token('text_secondary')))
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                         self.empty_title)
        if self.empty_body:
            body_rect = QRectF(token('space_5'), title_rect.bottom(),
                               bounds.width() - token('space_6'), token('space_6'))
            painter.setPen(_qcolor(token('text_tertiary')))
            painter.drawText(body_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop |
                             Qt.TextFlag.TextWordWrap, self.empty_body)
        painter.end()


class _DraggableTitleBar(QWidget):
    """Native system-move title bar shared by frameless app windows and dialogs."""

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            handle = self.window().windowHandle()
            if handle is not None and handle.startSystemMove():
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        toggle = getattr(self.window(), 'toggle_max', None)
        if event.button() == Qt.MouseButton.LeftButton and callable(toggle):
            toggle()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


class GlassDialog(QDialog):
    """Themed, modal dialog with focus containment and reduced-motion-aware entry."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setObjectName('glassDialog')
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.header = _DraggableTitleBar(self)
        self.header.setObjectName('titleBar')
        self.header.setFixedHeight(int(token('titlebar_height')))
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(token('space_4'), token('space_0'), token('space_2'), token('space_0'))
        header_layout.setSpacing(token('space_2'))
        self.dialog_title = label('', 'subtitle')
        self.dialog_title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        header_layout.addWidget(self.dialog_title)
        header_layout.addStretch()
        self.close_button = button('', self.reject, glyph='close', variant='titlebar')
        self.close_button.setAccessibleName(tr('Close'))
        self.close_button.setToolTip(tr('Close'))
        header_layout.addWidget(self.close_button)
        self._header_inserted = False
        self.opacity = QGraphicsOpacityEffect(self)
        self.opacity.setOpacity(1.0)
        self.setGraphicsEffect(self.opacity)
        self._fade = QPropertyAnimation(self.opacity, b'opacity', self)
        self._fade.setDuration(duration('slow'))
        self._fade.setEasingCurve(_curve('decelerate'))

    def setWindowTitle(self, title):
        super().setWindowTitle(tr(title))
        if hasattr(self, 'dialog_title'):
            self.dialog_title.setText(tr(title))

    def showEvent(self, event):
        if self.layout() is not None and not self._header_inserted:
            self.layout().insertWidget(0, self.header)
            self._header_inserted = True
        super().showEvent(event)
        if reduce_motion():
            self.opacity.setOpacity(1.0)
            return
        self.opacity.setOpacity(0.0)
        self._fade.setDuration(duration('slow'))
        self._fade.stop()
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.start()


class Toast(QFrame):
    """Small in-app notification with semantic edge, timeout and hover pause."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('toast')
        self.setProperty('toastTone', 'info')
        self._remaining = int(token('toast_duration'))
        self.setFixedWidth(int(token('space_7')) * 8)
        self.effect = QGraphicsOpacityEffect(self)
        self.effect.setOpacity(0.0)
        self.setGraphicsEffect(self.effect)
        self.box = QHBoxLayout(self)
        self.box.setContentsMargins(token('space_4'), token('space_3'), token('space_4'), token('space_3'))
        self.box.setSpacing(token('space_3'))
        self.message = QLabel()
        self.message.setWordWrap(True)
        self.message.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.box.addWidget(self.message, 1)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.dismiss)
        self._animations = QParallelAnimationGroup(self)
        self._opacity_anim = QPropertyAnimation(self.effect, b'opacity', self._animations)
        self._pos_anim = QPropertyAnimation(self, b'pos', self._animations)
        self._animations.addAnimation(self._opacity_anim)
        self._animations.addAnimation(self._pos_anim)
        self._animations.finished.connect(self._finish_animation)
        self.hide()

    def show_message(self, message, tone='info', timeout=None):
        self.setProperty('toastTone', tone if tone in {'success', 'warning', 'danger', 'info'} else 'info')
        self.setProperty('rtl', bool(self.parentWidget() and
                                    self.parentWidget().layoutDirection() == Qt.LayoutDirection.RightToLeft))
        self.style().unpolish(self)
        self.style().polish(self)
        self.message.setText(message)
        self._remaining = int(timeout or token('toast_duration'))
        self.adjustSize()
        target = self._target_pos()
        self.move(target + self._enter_offset())
        self.effect.setOpacity(0.0)
        self.show()
        self.raise_()
        self._animate(target, 0.0, 1.0)
        self.timer.start(self._remaining)

    def _target_pos(self):
        parent = self.parentWidget()
        if parent is None:
            return self.pos()
        margin = int(token('space_4'))
        x = parent.width() - self.width() - margin
        y = parent.height() - self.height() - margin
        if parent.layoutDirection() == Qt.LayoutDirection.RightToLeft:
            x = margin
        return QPointF(x, y).toPoint()

    def _enter_offset(self):
        direction = -1 if self.parentWidget() and self.parentWidget().layoutDirection() == Qt.LayoutDirection.RightToLeft else 1
        return QPointF(direction * token('space_6'), 0).toPoint()

    def _animate(self, target, start_opacity, end_opacity):
        self._animations.stop()
        if reduce_motion():
            self.effect.setOpacity(end_opacity)
            self.move(target)
            if end_opacity == 0:
                self.hide()
            return
        self._opacity_anim.setDuration(duration('slow'))
        self._opacity_anim.setEasingCurve(_curve('decelerate' if end_opacity else 'accelerate'))
        self._opacity_anim.setStartValue(start_opacity)
        self._opacity_anim.setEndValue(end_opacity)
        self._pos_anim.setDuration(duration('slow'))
        self._pos_anim.setEasingCurve(_curve('decelerate' if end_opacity else 'accelerate'))
        self._pos_anim.setStartValue(self.pos())
        self._pos_anim.setEndValue(target)
        self._animations.start()

    def _finish_animation(self):
        if self.effect.opacity() <= 0.0:
            self.hide()

    def dismiss(self):
        self.timer.stop()
        self._animate(self.pos() + self._enter_offset(), self.effect.opacity(), 0.0)

    def enterEvent(self, event):
        if self.timer.isActive():
            self._remaining = self.timer.remainingTime()
            self.timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.isVisible() and self._remaining > 0:
            self.timer.start(self._remaining)
        super().leaveEvent(event)

    def reposition(self):
        if self.isVisible():
            self.move(self._target_pos())


class GlassWindow(QWidget):
    def __init__(self, title, minimum=None):
        super().__init__()
        if minimum is None:
            minimum = (int(token('window_min_width')), int(token('window_min_height')))
        self.setWindowTitle(tr(title))
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(*minimum)
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(token('space_3'), token('space_2'), token('space_3'), token('space_3'))
        self.root.setSpacing(token('space_0'))
        self.titlebar = _DraggableTitleBar(self)
        self.titlebar.setObjectName('titleBar')
        self.titlebar.setFixedHeight(int(token('titlebar_height')))
        bar = QHBoxLayout(self.titlebar)
        bar.setContentsMargins(token('space_3'), token('space_0'), token('space_2'), token('space_0'))
        bar.setSpacing(token('space_1'))
        self.title_label = label(title, 'caption')
        self.title_label.setWordWrap(False)
        self.title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        bar.addWidget(self.title_label)
        bar.addStretch()
        controls = [
            ('minimize', self.showMinimized, 'Minimize', False),
            ('maximize', self.toggle_max, 'Maximize', False),
            ('close', self.close, 'Close', True),
        ]
        self.window_buttons = []
        for glyph, action, accessible_name, is_close in controls:
            btn = button('', action, glyph=glyph, variant='titlebar')
            btn.setAccessibleName(tr(accessible_name))
            btn.setToolTip(tr(accessible_name))
            btn.setProperty('windowButton', True)
            btn.setProperty('windowClose', is_close)
            btn.refresh_icon()
            bar.addWidget(btn)
            self.window_buttons.append(btn)
        self.root.addWidget(self.titlebar)
        self.grip = QSizeGrip(self)
        self.grip.setFixedSize(token('space_3'), token('space_3'))

    def toggle_max(self):
        self.showNormal() if self.isMaximized() else self.showMaximized()

    def set_title(self, text):
        self.title_label.setText(tr(text))

    def resizeEvent(self, event):
        self.grip.move(self.width() - token('space_5'), self.height() - token('space_5'))
        toast = getattr(self, 'toast', None)
        if toast is not None:
            toast.reposition()
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        pos = event.position()
        edges = Qt.Edges()
        if pos.x() < token('space_2'):
            edges |= Qt.Edge.LeftEdge
        if pos.x() > self.width() - token('space_2'):
            edges |= Qt.Edge.RightEdge
        if pos.y() < token('space_2'):
            edges |= Qt.Edge.TopEdge
        if pos.y() > self.height() - token('space_2'):
            edges |= Qt.Edge.BottomEdge
        if edges and self.windowHandle():
            self.windowHandle().startSystemResize(edges)
        else:
            super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        inset = float(token('border_inset'))
        rect = QRectF(self.rect()).adjusted(inset, inset, -inset, -inset)
        path = QPainterPath()
        radius = float(token('radius_xl'))
        path.addRoundedRect(rect, radius, radius)
        gradient = QLinearGradient(
            rect.topLeft(),
            QPointF(self.width() * float(token('window_gradient_x')),
                    self.height() * float(token('window_gradient_y'))))
        gradient.setColorAt(0, _qcolor(token('bg_layer1')))
        gradient.setColorAt(.5, _qcolor(token('bg_layer2')))
        gradient.setColorAt(1, _qcolor(token('bg_base')))
        painter.fillPath(path, gradient)
        painter.save()
        painter.setClipPath(path)
        radius_mesh = max(self.width(), self.height()) * float(token('window_mesh_radius_ratio'))
        violet = QRadialGradient(QPointF(rect.left(), rect.top()), radius_mesh)
        violet_color = _qcolor(token('mesh_violet'))
        violet.setColorAt(0, violet_color)
        violet.setColorAt(1, QColor(violet_color.red(), violet_color.green(), violet_color.blue(), 0))
        painter.fillRect(rect, violet)
        blue = QRadialGradient(QPointF(rect.right(), rect.bottom()), radius_mesh)
        blue_color = _qcolor(token('mesh_blue'))
        blue.setColorAt(0, blue_color)
        blue.setColorAt(1, QColor(blue_color.red(), blue_color.green(), blue_color.blue(), 0))
        painter.fillRect(rect, blue)
        painter.restore()
        painter.setPen(QPen(_qcolor(token('border_default')), float(token('border_width'))))
        painter.drawPath(path)
        painter.end()


def set_rtl(root, enabled):
    """Set layout direction and a repolished dynamic flag for direction-aware QSS."""
    direction = Qt.LayoutDirection.RightToLeft if enabled else Qt.LayoutDirection.LeftToRight
    root.setLayoutDirection(direction)
    for widget in (root, *root.findChildren(QWidget)):
        widget.setProperty('rtl', bool(enabled))
        style = widget.style()
        style.unpolish(widget)
        style.polish(widget)
        widget.update()


def scroll(widget):
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setWidget(widget)
    area.setFrameShape(QFrame.Shape.NoFrame)
    area.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    return area
