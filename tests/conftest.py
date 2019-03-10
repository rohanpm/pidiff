import functools
import sys
import pytest

from pidiff import dump_module, diff, DiffOptions

from . import checklogs


@pytest.fixture
def assert_logs_ok(request, caplog, tmpdir):
    yield functools.partial(checklogs, request.node.name, caplog, str(tmpdir))


@pytest.fixture
def diff_report_tester(assert_logs_ok):
    def fn(name):
        api1 = dump_module('tests.test_api.%s1' % name)
        api2 = dump_module('tests.test_api.%s2' % name)

        opts = DiffOptions()
        opts.full_symbol_names = True

        diff(api1, api2, opts)
        assert_logs_ok()

    yield fn


@pytest.fixture(autouse=True)
def restore_argv():
    orig_argv = sys.argv
    sys.argv = sys.argv[:]
    yield
    sys.argv = orig_argv
