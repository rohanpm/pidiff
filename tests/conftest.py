import functools
import sys
import os
import pytest

from pidiff import dump_module, diff, DiffOptions

from . import checklogs


@pytest.fixture
def assert_logs_ok(request, caplog, tmpdir):
    yield functools.partial(checklogs, request.node.name, caplog, str(tmpdir))


@pytest.fixture
def diff_report_tester(assert_logs_ok):
    def fn(name, set_enabled=None, set_disabled=None):
        api1 = dump_module('tests.test_api.%s1' % name)
        api2 = dump_module('tests.test_api.%s2' % name)

        opts = DiffOptions()
        opts.full_symbol_names = True

        for check in (set_enabled or []):
            opts.set_enabled(check)
        for check in (set_disabled or []):
            opts.set_disabled(check)

        diff(api1, api2, opts)
        assert_logs_ok()

    yield fn


@pytest.fixture(autouse=True)
def restore_argv():
    orig_argv = sys.argv
    sys.argv = sys.argv[:]
    yield
    sys.argv = orig_argv


@pytest.fixture(autouse=True)
def restore_cwd():
    orig_cwd = os.getcwd()
    yield
    if os.getcwd() != orig_cwd:
        os.chdir(orig_cwd)
