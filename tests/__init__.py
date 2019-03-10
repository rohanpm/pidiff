import os
import difflib


def data_path(*args):
    return os.path.join(os.path.dirname(__file__), 'data', *args)


def enforce_match():
    value = os.environ.get('UPDATE_BASELINES', '0')
    return value not in ('true', '1')


def assert_logs_equal(caplog, filename):
    messages = []
    for rec in caplog.records:
        messages.append(rec.message + '\n')

    with open(filename) as f:
        lines = f.readlines()

    diff = difflib.unified_diff(lines, messages, fromfile=filename, tofile='<test output>')
    diff = ''.join(diff)
    if diff:
        raise AssertionError("Output differs from expected\n%s" % diff)


def write_logs(caplog, filename):
    messages = []
    for rec in caplog.records:
        messages.append(rec.message + '\n')

    with open(filename, 'w') as f:
        f.writelines(messages)


def checklogs(name, caplog):
    logs_path = data_path(name + '_logs.txt')

    if enforce_match():
        assert_logs_equal(caplog, logs_path)
    else:
        write_logs(caplog, logs_path)
