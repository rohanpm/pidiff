import sys
import json

from pytest import raises

import pidiff._impl.schema as schema
import pidiff._impl.dump.command as command


def test_dump_command_notexist(capsys):
    """Dump command gives a specific exit code and message if asked
    to dump a nonexistent module.
    """
    sys.argv = ['cmd', 'some_nonexist_module']

    with raises(SystemExit) as exc:
        command.main()

    assert exc.value.code == 32

    (_, err) = capsys.readouterr()
    assert "No module named 'some_nonexist_module'" in err


def test_dump_command_typical(capsys):
    """Dump command dumps a module as JSON to stdout"""
    sys.argv = ['cmd', 'tests.test_api.api1']

    command.main()

    (out, err) = capsys.readouterr()

    # It should have no error
    assert not err

    # It should output JSON
    dump = json.loads(out)

    # It should be a valid API dump
    schema.validate(dump)
