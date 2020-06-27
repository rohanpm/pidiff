from pidiff._impl.command import argparser, PipArgs

PARSER = argparser()


def test_all_pip_args():
    parsed = PARSER.parse_args(
        [
            "--requirement",
            "abc",
            "--requirement",
            "def",
            "--constraint",
            "aaa",
            "-c",
            "bbb",
            "--pre",
            "--index-url",
            "idx1",
            "--extra-index-url",
            "idx2",
            "--extra-index-url",
            "idx3",
            "--pip-args",
            "arg1 'arg 2' other-arg",
            "src1",
            "src2",
        ]
    )

    pipargs = PipArgs(parsed)

    assert pipargs.excluding_requirements == [
        "-i",
        "idx1",
        "--extra-index-url",
        "idx2",
        "--extra-index-url",
        "idx3",
        "arg1",
        "arg 2",
        "other-arg",
    ]
    assert pipargs.all == pipargs.excluding_requirements + [
        "-r",
        "abc",
        "-r",
        "def",
        "-c",
        "aaa",
        "-c",
        "bbb",
        "--pre",
    ]


def test_empty_pip_args():
    parsed = PARSER.parse_args(["src1", "src2",])

    pipargs = PipArgs(parsed)

    assert pipargs.excluding_requirements == []
    assert pipargs.all == []

