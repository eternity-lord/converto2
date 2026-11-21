"""Obsidian Glass design tokens shared by every Qt widget and custom painter.

Change ``ACCENT`` below to rebrand the application; hover, pressed, gradient and
soft/glow variants are derived from it. Runtime palette selection is intentionally
limited to the UI layer and does not touch encoding or persisted media data.
"""
from __future__ import annotations

import os
import sys


ACCENT = '#7C6CFF'


def _rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _hex(rgb: tuple[int, int, int]) -> str:
    return '#' + ''.join(f'{max(0, min(255, v)):02X}' for v in rgb)


def _offset(value: str, delta: tuple[int, int, int]) -> str:
    return _hex(tuple(channel + change for channel, change in zip(_rgb(value), delta)))


def _rgba(value: str, opacity: float) -> str:
    r, g, b = _rgb(value)
    return f'rgba({r}, {g}, {b}, {round(max(0, min(1, opacity)) * 255)})'


ACCENT_HOVER = _offset(ACCENT, (18, 20, 0))
ACCENT_PRESSED = _offset(ACCENT, (-20, -20, -23))
ACCENT_GRADIENT_END = _offset(ACCENT, (-45, 32, 0))

SPACING = {
    'space_0': 0,
    'space_half': 2,
    'space_1': 4,
    'space_2': 8,
    'space_3': 12,
    'space_4': 16,
    'space_5': 24,
    'space_6': 32,
    'space_7': 48,
}

RADII = {
    'radius_sm': 6,
    'radius_md': 10,
    'radius_lg': 14,
    'radius_xl': 20,
    'radius_full': 999,
}

SIZES = {
    'font_caption': 11,
    'font_body': 13,
    'font_subtitle': 15,
    'font_title': 20,
    'font_display': 28,
    'font_number': 30,
    'line_body': 1.5,
    'line_title': 1.2,
    'weight_regular': 400,
    'weight_medium': 500,
    'weight_semibold': 600,
    'weight_bold': 700,
    'button_s': 28,
    'button_m': 36,
    'button_l': 44,
    'button_padding_x': 16,
    'button_icon': 16,
    'button_icon_gap': 8,
    'button_size_small': 28,
    'button_size_medium': 36,
    'button_size_large': 44,
    'loading_spinner_size': 16,
    'loading_spinner_stroke': 2,
    'loading_spinner_arc': 270,
    'loading_spinner_step': 6,
    'qt_angle_units': 16,
    'border_width': 1,
    'border_inset': 0.5,
    'indicator_width': 3,
    'indicator_height': 2,
    'radio_inner_border': 4,
    'slider_handle_margin': -6,
    'frame_interval': 16,
    'icon_s': 16,
    'icon_m': 20,
    'icon_l': 24,
    'icon_stroke': 1.5,
    'icon_grid': 18,
    'input_height': 36,
    'input_padding_x': 12,
    'checkbox_size': 18,
    'radio_size': 18,
    'toggle_width': 40,
    'toggle_height': 22,
    'toggle_knob': 16,
    'slider_track': 4,
    'slider_knob': 16,
    'titlebar_height': 40,
    'titlebar_button_width': 44,
    'titlebar_button_height': 32,
    'sidebar_width': 240,
    'sidebar_collapsed_width': 64,
    'navigation_height': 40,
    'navigation_icon': 20,
    'nav_indicator_height': 24,
    'table_row_height': 44,
    'progress_height': 6,
    'scrollbar_width': 6,
    'scrollbar_hover_width': 10,
    'tooltip_delay': 500,
    'toast_duration': 5000,
    'window_min_width': 1100,
    'window_min_height': 720,
    'window_default_width': 1400,
    'window_default_height': 900,
    'monitor_default_width': 350,
    'monitor_default_height': 180,
    'encoding_default_width': 1240,
    'encoding_default_height': 840,
    'details_dialog_width': 760,
    'details_dialog_height': 430,
    'preview_width': 285,
    'preview_height': 160,
    'table_status_width': 300,
    'dashboard_table_height': 180,
    'queue_table_min_height': 150,
    'chart_card_height': 235,
    'chart_min_height': 144,
    'encoding_chart_min_height': 65,
    'encoding_chart_max_height': 90,
    'search_max_width': 340,
    'job_filter_min_width': 190,
    'log_refresh_interval': 350,
    'queue_refresh_interval': 500,
    'metrics_refresh_interval': 1000,
    'log_detail_max_height': 170,
    'log_file_max_width': 330,
    'card_padding': 16,
    'card_spacing': 12,
    'chart_grid_lines': 5,
    'chart_glow_opacity': 0.25,
    'chart_headroom': 1.15,
    'skeleton_shimmer_width': 0.35,
    'window_gradient_x': 0.72,
    'window_gradient_y': 0.9,
    'window_mesh_radius_ratio': 0.58,
    'shimmer_step': 0.025,
    'button_hover_scale': 0.015,
    'button_press_scale': 0.03,
    'button_hover_lift': 1,
    'progress_shimmer_indeterminate': 0.28,
    'progress_shimmer_offset': 0.25,
    'progress_shimmer_width': 0.45,
    'chart_left_padding': 36,
    'chart_top_padding': 16,
    'chart_right_padding': 20,
    'chart_bottom_padding': 44,
    'focus_width': 2,
    'focus_gap': 2,
}

ELEVATION = {
    'shadow_e1': 'rgba(0, 0, 0, 102)',
    'shadow_e1_blur': 2,
    'shadow_e1_y': 1,
    'shadow_e2': 'rgba(0, 0, 0, 115)',
    'shadow_e2_blur': 12,
    'shadow_e2_y': 4,
    'shadow_e3': 'rgba(0, 0, 0, 140)',
    'shadow_e3_blur': 32,
    'shadow_e3_y': 12,
    'shadow_e4': 'rgba(0, 0, 0, 166)',
    'shadow_e4_blur': 64,
    'shadow_e4_y': 24,
}

MOTION = {
    'instant': 90,
    'fast': 150,
    'base': 220,
    'slow': 320,
    'ripple': 450,
    'page_stagger': 40,
    'standard': (0.2, 0.0, 0.0, 1.0),
    'decelerate': (0.0, 0.0, 0.0, 1.0),
    'accelerate': (0.3, 0.0, 1.0, 1.0),
    'spring': (0.34, 1.56, 0.64, 1.0),
    'reduce_motion': 100,
}


def _palette(theme: str) -> dict[str, object]:
    common = {
        'accent': ACCENT,
        'accent_hover': ACCENT_HOVER,
        'accent_pressed': ACCENT_PRESSED,
        'accent_gradient_start': ACCENT,
        'accent_gradient_end': ACCENT_GRADIENT_END,
        'accent_soft': _rgba(ACCENT, 0.14),
        'accent_glow': _rgba(ACCENT, 0.35),
        'accent_secondary': '#22D3EE',
        'success': '#34D399',
        'warning': '#FBBF24',
        'danger': '#F87171',
        'info': '#22D3EE',
        'success_soft': _rgba('#34D399', 0.14),
        'warning_soft': _rgba('#FBBF24', 0.14),
        'danger_soft': _rgba('#F87171', 0.14),
        'info_soft': _rgba('#38BDF8', 0.14),
        'danger_border': _rgba('#F87171', 0.30),
        'window_close_hover': '#C42B1C',
        'text_on_accent': '#FFFFFF',
        'mesh_violet': _rgba(ACCENT, 0.06),
        'mesh_blue': _rgba(ACCENT_GRADIENT_END, 0.06),
        'ripple': _rgba('#FFFFFF', 0.20),
        'inner_highlight': _rgba('#FFFFFF', 0.04),
        'ghost_hover': _rgba('#FFFFFF', 0.06),
        'ghost_pressed': _rgba('#FFFFFF', 0.10),
        'shimmer': _rgba('#FFFFFF', 0.26),
        'overlay': 'rgba(0, 0, 0, 140)',
        'close_hover_text': '#FFFFFF',
        'icon_active': ACCENT_HOVER,
    }
    if theme == 'light':
        surfaces = {
            'bg_base': '#F6F6FA',
            'bg_layer1': '#FFFFFF',
            'bg_layer2': '#FFFFFF',
            'bg_layer3': '#F1F1F7',
            'bg_hover': '#E7E7F0',
            'bg_pressed': '#DCDCE7',
            'border_subtle': 'rgba(20, 20, 28, 15)',
            'border_default': 'rgba(20, 20, 28, 26)',
            'border_strong': 'rgba(20, 20, 28, 41)',
            'text_primary': '#14141C',
            'text_secondary': '#555568',
            'text_tertiary': '#747487',
            'text_disabled': '#A1A1AF',
            'grid': '#E7E7EF',
            'glass_surface': 'rgba(255, 255, 255, 242)',
            'glass_border': 'rgba(20, 20, 28, 26)',
            'preview_surface': '#ECECF3',
            'chart_line': ACCENT,
            'chart_fill': _rgba(ACCENT, 0.16),
            'card_glow': _rgba(ACCENT, 0.06),
            'shadow_color': 'rgba(20, 20, 28, 26)',
            'focus_ring': _rgba(ACCENT, 0.25),
            'table_alt': '#FAFAFC',
            'tooltip_surface': '#FFFFFF',
            'menu_surface': 'rgba(255, 255, 255, 248)',
        }
    else:
        surfaces = {
            'bg_base': '#0B0B10',
            'bg_layer1': '#111118',
            'bg_layer2': '#17171F',
            'bg_layer3': '#1E1E28',
            'bg_hover': '#252532',
            'bg_pressed': '#2C2C3B',
            'border_subtle': 'rgba(255, 255, 255, 15)',
            'border_default': 'rgba(255, 255, 255, 26)',
            'border_strong': 'rgba(255, 255, 255, 41)',
            'text_primary': '#F4F4F8',
            'text_secondary': '#A1A1B5',
            'text_tertiary': '#6E6E85',
            'text_disabled': '#4A4A5C',
            'grid': '#22222D',
            'glass_surface': 'rgba(17, 17, 24, 242)',
            'glass_border': 'rgba(255, 255, 255, 26)',
            'preview_surface': '#111118',
            'chart_line': ACCENT_HOVER,
            'chart_fill': _rgba(ACCENT, 0.22),
            'card_glow': _rgba(ACCENT, 0.08),
            'shadow_color': 'rgba(0, 0, 0, 102)',
            'focus_ring': _rgba(ACCENT, 0.25),
            'table_alt': '#14141C',
            'tooltip_surface': '#1E1E28',
            'menu_surface': 'rgba(23, 23, 31, 248)',
        }
    return {**common, **surfaces, **SPACING, **RADII, **SIZES, **ELEVATION, **MOTION}


THEMES = {'dark': _palette('dark'), 'light': _palette('light')}
_ACTIVE_THEME = 'dark'
_REDUCE_MOTION = False


def set_active_theme(theme: str) -> str:
    global _ACTIVE_THEME
    _ACTIVE_THEME = 'light' if theme == 'light' else 'dark'
    return _ACTIVE_THEME


def active_theme() -> str:
    return _ACTIVE_THEME


def tokens(theme: str | None = None) -> dict[str, object]:
    return THEMES.get(theme or _ACTIVE_THEME, THEMES[_ACTIVE_THEME])


def token(name: str, theme: str | None = None):
    return tokens(theme)[name]


def set_reduce_motion(enabled: bool) -> None:
    global _REDUCE_MOTION
    _REDUCE_MOTION = bool(enabled)


def reduce_motion() -> bool:
    return _REDUCE_MOTION


def duration(name: str) -> int:
    values = tokens()
    if _REDUCE_MOTION and name not in ('reduce_motion', 'instant'):
        return int(values['reduce_motion'])
    if _REDUCE_MOTION and name == 'instant':
        return int(values['reduce_motion'])
    return int(values[name])


def motion_easing(name: str) -> tuple[float, float, float, float]:
    return tokens()[name]


def windows_reduce_motion() -> bool:
    """Read Windows' animation accessibility switch; allow a test/user override."""
    override = os.environ.get('QT_REDUCE_MOTION')
    if override is not None:
        return override.strip().lower() in {'1', 'true', 'yes', 'on'}
    if sys.platform == 'win32':
        try:
            import ctypes
            enabled = ctypes.c_int(1)
            # SPI_GETCLIENTAREAANIMATION reports whether client-area animations are on.
            if ctypes.windll.user32.SystemParametersInfoW(0x1042, 0, ctypes.byref(enabled), 0):
                return enabled.value == 0
        except (AttributeError, OSError):
            pass
    return False


def elevation(name: str) -> tuple[object, int, int]:
    values = tokens()
    return values[f'shadow_{name}'], int(values[f'shadow_{name}_blur']), int(values[f'shadow_{name}_y'])
