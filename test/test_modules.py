import pytest

def test_module_pytube():
    import pytube
    assert pytube.__title__ == 'pytube3'