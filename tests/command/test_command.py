import sys
import logging
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


def fake_popen(*args, **kwargs):
    cmd = args[0]

    if cmd[0] == 'virtualenv':
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

    if 'import distutils.sysconfig' in ''.join(cmd):
        return real_popen(*args, **kwargs)

    if cmd[1:3] == ['-m', 'pidiff._impl.dump.command']:
        root_name = cmd[3]
        if '/s1/' in cmd[0]:
            root_name = root_name + '1'
        else:
            root_name = root_name + '2'
        return mock_popen_from_dump(root_name, *args, **kwargs)

    raise AssertionError("Don't know what to do with command %s" % cmd)


@mark.parametrize('testapi,exitcode,extra_args', [
    ('nochange', 0, []),
    ('minorbad', 88, ['-v']),
    ('minorgood', 0, []),
    ('major', 99, ['--full-symbol-names']),
    ('force_error', 64, []),
])
def test_typical_diff(workdir, testapi, exitcode, extra_args, caplog):
    sys.argv = ['pidiff', '--workdir', workdir,
                'foopkg==1.0.0', 'foopkg==1.1.0', 'tests.test_api.%s' % testapi]
    sys.argv.extend(extra_args)

    caplog.set_level(logging.INFO)

    with mock.patch('subprocess.Popen') as mock_popen:
        mock_popen.side_effect = fake_popen
        with raises(SystemExit) as exc:
            command.main()

    checklogs('typical_diff_%s' % testapi, caplog, workdir)

    assert exc.value.code == exitcode
