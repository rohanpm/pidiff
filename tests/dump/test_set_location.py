from unittest import mock

from pidiff._impl.dump.dump import set_location


def test_set_location_tolerates_errors():
    out = {}
    with mock.patch("pidiff._impl.dump.dump.get_file") as get_file:
        get_file.return_value = "somefile"
        set_location(out, print)

    # It should have reached here without raising

    # It should have set file (but not lineno)
    assert out == {"file": "somefile"}
