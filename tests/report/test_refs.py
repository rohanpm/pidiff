from pidiff.dump import dump_module
from pidiff.diff import diff


def test_multiple_refs(assert_logs_ok):
    """Generated log output is reasonable when dealing with
    symbols referenced from multiple locations
    """

    api1 = dump_module('tests.test_api.multiname1')
    api2 = dump_module('tests.test_api.multiname2')

    diff(api1, api2)
    assert_logs_ok()
