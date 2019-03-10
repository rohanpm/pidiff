import enum
import logging

DIFFLOG = logging.getLogger('pidiff.diff')


class ChangeType(enum.IntEnum):
    # These should be ordered in increasing level of severity
    NONE = 0
    INFO = 1
    MINOR = 2
    MAJOR = 3


class ErrorCode:
    LEVEL = logging.INFO
    CHANGE_TYPE = ChangeType.INFO

    def __init__(self, errcode, template):
        self.errcode = errcode
        self.template = template

    def log(self, sym_old, sym_new, old_location, new_location, **kwargs):
        message = self.template.format(
            sym_old=sym_old, sym_new=sym_new, extra=kwargs)

        new_filename = sym_new.display_file
        new_lineno = sym_new.lineno
        if (not new_filename) or new_filename.startswith(('.', '/')):
            (new_filename, new_lineno) = new_location

        # old_filename = sym_old.display_file
        # old_lineno = sym_old.lineno
        # if (not old_filename) or old_filename.startswith(('.', '/')):
        #     (old_filename, old_lineno) = old_location

        DIFFLOG.log(self.LEVEL,
                    "%s:%s: %s %s",
                    new_filename,
                    new_lineno,
                    self.errcode,
                    message,
                    extra=dict(change_type=self.CHANGE_TYPE))


class MajorCode(ErrorCode):
    LEVEL = logging.ERROR
    CHANGE_TYPE = ChangeType.MAJOR


class MinorCode(ErrorCode):
    LEVEL = logging.ERROR
    CHANGE_TYPE = ChangeType.MINOR


class Codes:
    RemovedSym = MajorCode(
        "D100",
        "{sym_old.ob.object_type} removed: {sym_old.display_name}",
    )
    RemovedArg = MajorCode(
        "D101",
        "argument removed from {sym_new.display_name}: {extra[arg_name]}"
    )
    AddedSym = MinorCode(
        "D200",
        "{sym_new.ob.object_type} added: {sym_new.display_name}")

    NoLongerCallable = MajorCode(
        "D300",
        "no longer callable: {sym_new.display_name}")
