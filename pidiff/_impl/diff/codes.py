import enum
import logging

DIFFLOG = logging.getLogger("pidiff.diff")


class ChangeType(enum.IntEnum):
    """Enum representing types of API changes.

    This is an integer enum, with values given in increasing
    level of severity.
    """

    NONE = 0
    """int: No interface changes."""

    # Reserved for now...
    # INFO = 100

    MINOR = 200
    """int: Minor interface changes; new but backwards-compatible functionality."""

    MAJOR = 300
    """int: Major interface changes; functionality was removed or changed in a
    backwards-incompatible manner.
    """


class LoggingContext:
    # A context for log messages produced during a diff which
    # performs de-duplication.

    def __init__(self):
        self._logged = set()

    def _filter(self, record):
        log_key = (record.getMessage(), record.levelname)
        if log_key not in self._logged:
            self._logged.add(log_key)
            return True
        return 0

    def __enter__(self):
        DIFFLOG.addFilter(self._filter)
        return self

    def __exit__(self, *_args, **_kwargs):
        DIFFLOG.removeFilter(self._filter)


class ErrorCode:
    LEVEL = logging.INFO
    CHANGE_TYPE = ChangeType.MAJOR

    def __init__(self, errcode, errname, template):
        self.errcode = errcode
        self.errname = errname
        self.template = template

    def log(self, sym_old, sym_new, old_location, new_location, **kwargs):
        message = self.template.format(sym_old=sym_old, sym_new=sym_new, extra=kwargs)

        new_filename = sym_new.display_file
        new_lineno = sym_new.lineno
        if (not new_filename) or new_filename.startswith((".", "/")):
            (new_filename, new_lineno) = new_location

        DIFFLOG.log(
            self.LEVEL,
            "%s:%s: %s %s",
            new_filename,
            new_lineno,
            self.errcode,
            message,
            extra=dict(change_type=self.CHANGE_TYPE),
        )


class MajorCode(ErrorCode):
    LEVEL = logging.ERROR
    CHANGE_TYPE = ChangeType.MAJOR


class MinorCode(ErrorCode):
    LEVEL = logging.ERROR
    CHANGE_TYPE = ChangeType.MINOR


class Codes:
    # Removals of symbols from API
    RemovedSym = MajorCode(
        "B100",
        "removed-object",
        "{sym_old.ob.object_type} removed: {sym_old.display_name}",
    )
    RemovedModule = MajorCode(
        "B110", "removed-module", "module removed: {sym_old.display_name}"
    )
    RemovedExternalModule = MajorCode(
        "B111",
        "removed-external-module",
        "external module removed: {sym_old.display_name}",
    )
    RemovedFunction = MajorCode(
        "B120", "removed-function", "function removed: {sym_old.display_name}"
    )
    RemovedMethod = MajorCode(
        "B130", "removed-method", "method removed: {sym_old.display_name}"
    )
    RemovedClass = MajorCode(
        "B140", "removed-class", "class removed: {sym_old.display_name}"
    )

    # Additions of symbols to API
    AddedSym = MinorCode(
        "N200", "added-object", "{sym_new.ob.object_type} added: {sym_new.display_name}"
    )
    AddedModule = MinorCode(
        "N210", "added-module", "module added: {sym_new.display_name}"
    )
    AddedExternalModule = MinorCode(
        "N211", "added-external-module", "external module added: {sym_new.display_name}"
    )
    AddedFunction = MinorCode(
        "N220", "added-function", "function added: {sym_new.display_name}"
    )
    AddedMethod = MinorCode(
        "N230", "added-method", "method added: {sym_new.display_name}"
    )
    AddedClass = MinorCode("N240", "added-class", "class added: {sym_new.display_name}")

    # Backwards-incompatible signature changes
    RemovedArg = MajorCode(
        "B300",
        "removed-argument",
        "argument(s) removed from {sym_new.display_name}: {extra[arg_name]}",
    )
    AddedArg = MajorCode(
        "B310",
        "added-argument",
        "argument(s) added to {sym_new.display_name}: {extra[arg_name]}",
    )
    MovedArg = MajorCode(
        "B320",
        "moved-argument",
        (
            "argument position changed in {sym_new.display_name}: "
            "{extra[arg_name]} ({extra[old_position]} => {extra[new_position]})"
        ),
    )
    UnpositionalArg = MajorCode(
        "B330",
        "unpositional-argument",
        (
            "argument in {sym_new.display_name} can no longer be passed positionally: "
            "{extra[arg_name]} (was position {extra[old_position]})"
        ),
    )
    RemovedVarArgs = MajorCode(
        "B340",
        "removed-var-args",
        "{sym_new.display_name} no longer accepts unlimited positional arguments",
    )
    RemovedVarKeywordArgs = MajorCode(
        "B350",
        "removed-var-keyword-args",
        "{sym_new.display_name} no longer accepts unlimited keyword arguments",
    )

    # Backwards-compatible signature changes
    AddedOptionalArg = MinorCode(
        "N400",
        "added-optional-argument",
        "optional argument(s) added to {sym_new.display_name}: {extra[arg_name]}",
    )
    AddedArgDefault = MinorCode(
        "N410",
        "added-argument-default",
        "default value added to {sym_new.display_name} argument: {extra[arg_name]}",
    )
    AddedVarArgs = MinorCode(
        "N440",
        "added-var-args",
        "{sym_new.display_name} now accepts unlimited positional arguments",
    )
    AddedVarKeywordArgs = MinorCode(
        "N450",
        "added-var-keyword-args",
        "{sym_new.display_name} now accepts unlimited keyword arguments",
    )

    # Other
    NoLongerCallable = MajorCode(
        "B800", "uncallable", "no longer callable: {sym_new.display_name}"
    )
