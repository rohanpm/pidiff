import os
from unittest import mock
from pytest import raises

from pidiff._impl.command import get_dist_name, detect_module


def test_get_dist_name_from_setup_py():
    fakedist = os.path.join(os.path.dirname(__file__), 'fakedist')
    assert get_dist_name(fakedist) == 'some_module'


def test_get_dist_name_from_string():
    assert get_dist_name('foo') == 'foo'
    assert get_dist_name('bar==1.0') == 'bar'
    assert get_dist_name('baz>=2.0') == 'baz'


def test_get_dist_name_fails():
    assert get_dist_name('./foo/bar/baz') is None


def test_detect_module_fails_pkg():
    with raises(SystemExit) as exc:
        detect_module(None, './somepkg', None, './otherpkg')
    assert exc.value.code == 32


def test_detect_module():
    s1env = mock.MagicMock()
    s2env = mock.MagicMock()

    s1env.dist_toplevel.return_value = 'some_top_level\n'

    detected = detect_module(s1env, 'pkg==1.0', s2env, 'pkg==2.0')

    assert detected == 'some_top_level'


def test_detect_module_multi_toplevel():
    s1env = mock.MagicMock()
    s2env = mock.MagicMock()

    s1env.dist_toplevel.return_value = None
    s2env.dist_toplevel.return_value = 'line1\nline2\n'

    with raises(SystemExit) as exc:
        detect_module(s1env, 'pkg==1.0', s2env, 'pkg==2.0')
    assert exc.value.code == 32
