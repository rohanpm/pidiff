import os
from unittest import mock

from pidiff._impl import command


def test_ensure_exists(tmpdir):
    path = str(tmpdir.join('test-path'))
    command.ensure_exists(path)
    command.ensure_exists(path)

    assert os.path.exists(path)


def test_cache(tmpdir, monkeypatch):
    cache = tmpdir.mkdir('cache')
    monkeypatch.setenv('XDG_CACHE_HOME', str(cache))

    cache_pidiff = cache.mkdir('pidiff')

    # Make some new dirs
    cache_pidiff.mkdir('newdir1')
    cache_pidiff.mkdir('newdir2')

    # Then some old dirs which should be removed
    cache_pidiff.mkdir('olddir1').setmtime(1000)
    cache_pidiff.mkdir('olddir2').setmtime(10000)

    # Now let's try getting path to a virtualenv
    args = mock.Mock()
    args.workdir = None

    path = command.make_venv_path('some-dist', args)

    # It should assemble same path again for same dist
    assert path == command.make_venv_path('some-dist', args)
    basename = os.path.basename(path)

    # Let's see what exists after that creation
    cache_dirs = [x.basename for x in cache_pidiff.listdir()]
    assert 'newdir1' in cache_dirs
    assert 'newdir2' in cache_dirs
    assert basename in cache_dirs

    # Nothing else present (old dirs should be cleaned)
    assert len(cache_dirs) == 3


def test_cache_uses_reqs(tmpdir, monkeypatch):
    cache = tmpdir.mkdir('cache')
    monkeypatch.setenv('XDG_CACHE_HOME', str(cache))

    dist = tmpdir.mkdir('dist')
    setup_py = dist.join('setup.py')
    setup_py.write('some content')

    args = mock.Mock()
    args.workdir = None

    path1 = command.make_venv_path(str(dist), args)

    # If setup.py content changes, cache path should also change
    setup_py.write('more content')

    path2 = command.make_venv_path(str(dist), args)

    assert os.path.exists(path1)
    assert os.path.exists(path2)
    assert path1 != path2


def test_cache_recreates(tmpdir, monkeypatch):
    cache = tmpdir.mkdir('cache')
    monkeypatch.setenv('XDG_CACHE_HOME', str(cache))

    args = mock.Mock()
    args.workdir = None

    path1 = command.make_venv_path('some-dist', args)

    # Make a subdir so we can verify it disappears later
    sub_path = os.path.join(path1, 'subdir')
    os.makedirs(sub_path)

    # Ask to make the same venv again, but this time with recreate
    args.recreate = True
    path2 = command.make_venv_path('some-dist', args)

    # It should make the same dir
    assert path1 == path2

    # It should have recreated the dir
    assert not os.path.exists(sub_path)


def test_clean_cache_swallows_errors():
    with mock.patch('glob.glob') as mock_glob:
        mock_glob.side_effect = OSError()
        # It should complete without raising
        command.cachedir()
