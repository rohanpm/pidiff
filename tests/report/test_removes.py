from pidiff.dump import dump_module
from pidiff.diff import diff


def test_remove_various(assert_logs_ok):
    api1 = dump_module('tests.test_api.api1')
    api2 = dump_module('tests.test_api.api2')

    diff(api1, api2)
    assert_logs_ok()
