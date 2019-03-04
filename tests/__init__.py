import os
import difflib


def data_path(*args):
    return os.path.join(os.path.dirname(__file__), 'data', *args)


def enforce_match():
    ci = os.environ.get('CI', '')
    return ci not in ('false', '0', '')


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

    if not messages:
        raise AssertionError("No log messages detected")

    with open(filename, 'w') as f:
        f.writelines(messages)


def checklogs(request, caplog):
    logs_path = data_path(request.node.name + '_logs.txt')

    if enforce_match():
        assert_logs_equal(caplog, logs_path)
    else:
        write_logs(caplog, logs_path)
