import enum
import logging

DIFFLOG = logging.getLogger('pidiff.diff')


class ChangeType(enum.IntEnum):
    # These should be ordered in increasing level of severity
    INFO = 0
    MINOR = 1
    MAJOR = 2


class ErrorCode:
    LEVEL = logging.INFO
    CHANGE_TYPE = ChangeType.INFO

    def __init__(self, errcode, template, force_lineno=None):
        self.errcode = errcode
        self.template = template
        self.force_lineno = force_lineno

    def lineno(self, api, parent):
        if self.force_lineno is not None:
            return self.force_lineno
        return api.lineno

    def log(self, sym_old, sym_new, **kwargs):
        message = self.template.format(
            sym_old=sym_old, sym_new=sym_new, extra=kwargs)
        DIFFLOG.log(self.LEVEL,
                    "%s:%s: %s %s",
                    (sym_new.display_file or sym_old.display_file),
                    sym_new.lineno,
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
