try:
    from ._impl.diff.codes import ChangeType
    from ._impl.diff.diff import diff, DiffOptions, DiffResult
    from ._impl.dump.dump import dump_module
except ModuleNotFoundError:  # pragma: no cover
    # Why: because we're imported by the dump command
    # within the virtualenvs used for test, and we don't
    # want to insist on all our own dependencies being available
    # there.
    pass

__all__ = ["diff", "dump_module", "DiffOptions", "DiffResult", "ChangeType"]
