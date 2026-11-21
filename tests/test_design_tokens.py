from app.ui.design_tokens import (
    active_theme,
    duration,
    reduce_motion,
    set_active_theme,
    set_reduce_motion,
    token,
    windows_reduce_motion,
)


def test_obsidian_glass_core_palette():
    assert token('bg_base', 'dark') == '#0B0B10'
    assert [token(f'bg_layer{i}', 'dark') for i in range(1, 4)] == [
        '#111118', '#17171F', '#1E1E28',
    ]
    assert token('text_primary', 'dark') == '#F4F4F8'
    assert token('text_secondary', 'dark') == '#A1A1B5'
    assert token('text_tertiary', 'dark') == '#6E6E85'
    assert token('accent', 'dark') == '#7C6CFF'
    assert token('accent_secondary', 'dark') == '#22D3EE'
    assert token('info', 'dark') == '#22D3EE'


def test_light_palette_and_active_theme_are_isolated():
    original = active_theme()
    try:
        assert token('bg_base', 'light') == '#F6F6FA'
        assert set_active_theme('light') == 'light'
        assert token('bg_base') == '#F6F6FA'
        assert token('bg_base', 'dark') == '#0B0B10'
    finally:
        set_active_theme(original)


def test_reduce_motion_duration_and_windows_override(monkeypatch):
    original = reduce_motion()
    try:
        set_reduce_motion(True)
        assert duration('slow') == token('reduce_motion')
        assert duration('instant') == token('reduce_motion')
        monkeypatch.setenv('QT_REDUCE_MOTION', '1')
        assert windows_reduce_motion()
        monkeypatch.setenv('QT_REDUCE_MOTION', '0')
        assert not windows_reduce_motion()
    finally:
        set_reduce_motion(original)
