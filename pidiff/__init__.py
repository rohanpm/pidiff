try:
    from .diff._codes import ChangeType
    from .diff._diff import diff
    from .dump._dump import dump_module
except ModuleNotFoundError:
    # Why: because we're imported by the dump command
    # within the virtualenvs used for test, and we don't
    # want to insist on all our own dependencies being available
    # there.
    pass

__all__ = ['diff', 'dump_module', 'ChangeType']
