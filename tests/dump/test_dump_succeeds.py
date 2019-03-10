import pytest

from pidiff.dump import dump_module


@pytest.mark.parametrize('api_name', [
    'tests.test_api.api1',
    'tests.test_api.api2',
    'tests.test_api.multiname1',
    'tests.test_api.multiname2',
    'tests.test_api.exc_ctor1',
    'tests.test_api.exc_ctor2',
])
def test_dump_succeeds(api_name):
    result = dump_module(api_name)

    # note we expect dump_module internally to validate
    # that its own output matches the schema
    assert result
