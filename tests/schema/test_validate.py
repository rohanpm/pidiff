from pytest import raises

from pidiff._impl.schema import validate, BadRefException


def test_validate_empty():
    """A simple empty dump validates OK"""
    validate({
        "root": {
            "name": "somemodule",
            "ref": "1234",
        },
        "objects": {
            "1234": {
                "is_external": False,
                "is_callable": False,
                "object_type": "object",
            }
        },
    })


def test_validate_bad_root_ref():
    """Validation fails if root object is not available"""
    with raises(BadRefException):
        validate({
            "root": {
                "name": "somemodule",
                "ref": "1234",
            },
            "objects": {
            },
        })


def test_validate_bad_object_ref():
    """Validation fails if other object is not available"""
    with raises(BadRefException):
        validate({
            "root": {
                "name": "somemodule",
                "ref": "1234",
            },
            "objects": {
                "1234": {
                    "is_external": False,
                    "is_callable": False,
                    "object_type": "object",
                    "children": [
                        {"name": "foobar",
                         "ref": "3456"},
                    ]
                }
            },
        })
