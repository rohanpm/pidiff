def test_remove_various(diff_report_tester):
    diff_report_tester('api')


def test_multiple_refs(diff_report_tester):
    """Generated log output is reasonable when dealing with
    symbols referenced from multiple locations
    """
    diff_report_tester('multiname')


def test_class_without_signature(diff_report_tester):
    """Tested API has classes where inspect.signature raises"""
    diff_report_tester('exc_ctor')


def test_signatures(diff_report_tester):
    diff_report_tester('signatures')
