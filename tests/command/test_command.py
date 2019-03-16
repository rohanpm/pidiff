import os
import sys
import logging
import tempfile
from unittest import mock
import json
from subprocess import Popen as real_popen, CalledProcessError

from pytest import fixture, raises, mark

from pidiff._impl import command
from pidiff import dump_module

from tests import checklogs


@fixture(scope='session')
def workdir(tmp_path_factory):
    return str(tmp_path_factory.mktemp('workdir'))


@fixture(autouse=True)
def restore_cwd():
    original_cwd = os.getcwd()
    yield
    new_cwd = os.getcwd()

    if original_cwd != new_cwd:
        os.chdir(original_cwd)


def test_help():
    """Running command with --help succeeds."""

    sys.argv = ['pidiff', '--help']
    with raises(SystemExit) as exc:
        command.main()

    assert exc.value.code == 0


def mock_popen_from_dump(root_name, *args, **kwargs):
    if 'force_error' in root_name:
        raise CalledProcessError(27, args[0])

    dumped = dump_module(root_name)

    assert 'stdout' in kwargs

    stdout = kwargs.pop('stdout')
    json.dump(dumped, stdout)

    return real_popen(['/bin/echo', 'intercepted dump of %s' % root_name])


def safe_command(cmd):
    if cmd[0] == 'virtualenv':
        return True

    if 'import distutils.sysconfig' in ''.join(cmd):
        return True

    if 'pkg_resources.get_distribution' in ''.join(cmd):
        return True


def fake_popen(*args, **kwargs):
    cmd = args[0]

    if safe_command(cmd):
        return real_popen(*args, **kwargs)

    if cmd[0:3] == ['bin/python', '-m', 'pip']:
        pip = cmd[3:]
        if pip == ['-V']:
            return real_popen(*args, **kwargs)

        if 'install' in pip:
            cmd = ['/bin/echo'] + cmd
            return real_popen(cmd, *args[1:], **kwargs)

        if 'freeze' in pip:
            return real_popen(*args, **kwargs)

    if cmd[1:3] == ['-m', 'pidiff._impl.dump.command']:
        root_name = cmd[3]
        if '/s1/' in cmd[0]:
            root_name = root_name + '1'
        else:
            root_name = root_name + '2'
        return mock_popen_from_dump(root_name, *args, **kwargs)

    raise AssertionError("Don't know what to do with command %s" % cmd)


@mark.parametrize('testapi,testname,exitcode,extra_args', [
    ('nochange', None, 0, []),
    ('minorbad', None, 88, ['-v']),
    ('minorbad', 'minorbad_disabled', 0, ['--disable', 'N220,B123']),
    ('minorgood', None, 0, ['--recreate']),
    ('major', None, 99, ['--full-symbol-names']),
    ('force_error', None, 64, []),
])
def test_typical_diff(workdir, testapi, testname, exitcode, extra_args, caplog):
    sys.argv = ['pidiff', '--workdir', workdir,
                'foopkg==1.0.0', 'foopkg==1.1.0', 'tests.test_api.%s' % testapi]
    sys.argv.extend(extra_args)

    caplog.set_level(logging.INFO)

    with mock.patch('subprocess.Popen') as mock_popen:
        mock_popen.side_effect = fake_popen
        with raises(SystemExit) as exc:
            command.main()

    testname = testname or testapi
    checklogs('typical_diff_%s' % testname, caplog, workdir)

    assert exc.value.code == exitcode


def test_missing_module(workdir):
    """Command fails if module name is not provided and autodetect fails"""
    sys.argv = ['pidiff', '--workdir', workdir, 'pkg1', 'pkg2']

    with mock.patch('subprocess.Popen') as mock_popen:
        mock_popen.side_effect = fake_popen
        with raises(SystemExit) as exc:
            command.main()

    assert exc.value.code == 32


def test_make_workdir_requested():
    assert command.make_workdir('some/path').name == 'some/path'


@mark.parametrize('existing_dir', ['.git', '.tox'])
def test_make_workdir_pidiff(tmpdir, existing_dir):
    os.chdir(str(tmpdir))

    tmpdir.mkdir(existing_dir)

    assert command.make_workdir(None).name == '.pidiff'


def test_make_workdir_tmpdir(tmpdir):
    os.chdir(str(tmpdir))

    assert isinstance(command.make_workdir(None), tempfile.TemporaryDirectory)
