import functools
import pytest

from . import checklogs


@pytest.fixture
def assert_logs_ok(request, caplog):
    yield functools.partial(checklogs, request, caplog)
