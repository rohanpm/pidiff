import copy

from pidiff._impl.dump.ast_enrich import AstEnricher


def test_enrich_ignores_errors(tmpdir):
    broken_file = tmpdir.join("broken.py")
    broken_file.write(
        """
        class Foo:
            oops, this isn't valid python
    """
    )

    valid_file = tmpdir.join("valid.py")
    valid_file.write(
        """
        class LineOne:
            pass
    """
    )

    dump = {
        "objects": {
            "1234": {"object_type": "class", "file": str(broken_file), "lineno": 1},
            # another object in same file as well,
            # to ensure code for cached errors is covered
            "1235": {"object_type": "class", "file": str(broken_file), "lineno": 5},
            # an object with missing file, so we can't even try to parse
            "1236": {"object_type": "class"},
            # an object with missing lineno, skipped since we can't possibly
            # match to a location
            "1237": {"object_type": "class", "file": "some_file.py"},
            # an object which can't be matched up with any class definition
            # in a successfully parsed file
            "1238": {"object_type": "class", "file": str(valid_file), "lineno": 20},
        }
    }

    dump_orig = copy.deepcopy(dump)

    enricher = AstEnricher()

    # It should not crash
    enricher.run(dump)

    # It should not affect the dump in any way
    assert dump == dump_orig
