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

    def __init__(self, errcode, errname, template):
        self.errcode = errcode
        self.errname = errname
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
    # Removals of symbols from API
    RemovedSym = MajorCode(
        "D100",
        "removed-object",
        "{sym_old.ob.object_type} removed: {sym_old.display_name}",
    )
    RemovedModule = MajorCode(
        "D110",
        "removed-module",
        "module removed: {sym_old.display_name}",
    )
    RemovedExternalModule = MajorCode(
        "D111",
        "removed-external-module",
        "external module removed: {sym_old.display_name}",
    )
    RemovedFunction = MajorCode(
        "D120",
        "removed-function",
        "function removed: {sym_old.display_name}",
    )
    RemovedMethod = MajorCode(
        "D130",
        "removed-method",
        "method removed: {sym_old.display_name}",
    )
    RemovedClass = MajorCode(
        "D140",
        "removed-class",
        "class removed: {sym_old.display_name}",
    )

    # Additions of symbols to API
    AddedSym = MinorCode(
        "D200",
        "added-object",
        "{sym_new.ob.object_type} added: {sym_new.display_name}")
    AddedModule = MinorCode(
        "D210",
        "added-module",
        "module added: {sym_new.display_name}")
    AddedExternalModule = MinorCode(
        "D211",
        "added-external-module",
        "external module added: {sym_new.display_name}")
    AddedFunction = MinorCode(
        "D220",
        "added-function",
        "function added: {sym_new.display_name}")
    AddedMethod = MinorCode(
        "D230",
        "added-method",
        "method added: {sym_new.display_name}")
    AddedClass = MinorCode(
        "D240",
        "added-class",
        "class added: {sym_new.display_name}")

    # Backwards-incompatible signature changes
    RemovedArg = MajorCode(
        "D300",
        "removed-argument",
        "argument(s) removed from {sym_new.display_name}: {extra[arg_name]}"
    )

    # Backwards-compatible signature changes
    AddedOptionalArg = MinorCode(
        "D400",
        "added-optional-argument",
        "optional argument(s) added to {sym_new.display_name}: {extra[arg_name]}"
    )

    # Other
    NoLongerCallable = MajorCode(
        "D800",
        "uncallable",
        "no longer callable: {sym_new.display_name}")
