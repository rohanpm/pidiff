import functools
import pytest  # type: ignore

from pidiff.dump import dump_module
from pidiff.diff import diff

from . import checklogs


@pytest.fixture
def assert_logs_ok(request, caplog):
    yield functools.partial(checklogs, request, caplog)


@pytest.fixture
def diff_report_tester(assert_logs_ok):
    def fn(name):
        api1 = dump_module('tests.test_api.%s1' % name)
        api2 = dump_module('tests.test_api.%s2' % name)

        diff(api1, api2)
        assert_logs_ok()

    yield fn
