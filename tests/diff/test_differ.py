import pytest

from pidiff._impl.diff.diff import Differ


def test_differ_getattr():
    differ = Differ(None, None, None)
    differ.location_stack_old.append(('somefile', 0))
    differ.location_stack_new.append(('somefile', 0))

    # Should be able to refer to any of the defined
    # codes by attribute
    assert callable(differ.AddedFunction)

    # But accessing something which doesn't exist
    # should raise
    with pytest.raises(AttributeError):
        differ.SomethingNonexistent
