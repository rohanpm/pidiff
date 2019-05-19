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


def test_signatures_with_options(diff_report_tester):
    diff_report_tester('signatures',
                       set_disabled=['N400', 'added-var-args', 'added-argument'],
                       set_enabled=['added-var-args'])


def test_add_external_module(diff_report_tester):
    diff_report_tester('externalmod')


def test_builtin(diff_report_tester):
    diff_report_tester('builtin')


def test_classprop(diff_report_tester):
    diff_report_tester('classprop')
