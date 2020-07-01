import logging
import functools
from typing import Optional, Set

import semver  # type: ignore

from .. import schema
from .codes import Codes, ChangeType, LoggingContext
from .api import Symbol


LOG = logging.getLogger("pidiff")


class StopDiff(Exception):
    """This exception is thrown when diffing of a particular
    symbol should be stopped, e.g. because differences already
    covered make further testing irrelevant.
    """


class Interceptor(logging.NullHandler):
    def __init__(self):
        super().__init__()
        self.max_change_type = ChangeType.NONE

    def handle(self, record):
        change_type = getattr(record, "change_type", None)
        if change_type is not None:
            self.max_change_type = max(change_type, self.max_change_type)


class CapturedLog:
    def __init__(self):
        self._handler = None

    def __enter__(self):
        self._handler = Interceptor()
        logging.getLogger("pidiff.diff").addHandler(self._handler)
        return self

    def __exit__(self, *args, **kwargs):
        assert self._handler
        logging.getLogger("pidiff.diff").removeHandler(self._handler)

    @property
    def max_change_type(self):
        return self._handler.max_change_type


class DiffOptions:
    """Options to be used for an interface diff."""

    def __init__(self):
        self.summarize = True
        """boolean: If True, a human-readable summary will be logged at the end
        of the diff."""

        self.full_symbol_names = False
        """boolean: if True, produced log messages will include fully qualified
        symbol names (e.g. ``mymodule.submodule.SomeClass``) rather than the
        default short names (e.g. ``SomeClass``).
        """

        self._enabled = set()
        self._disabled = set()

    def set_enabled(self, check: str) -> None:
        """Add a check to the set of enabled checks.

        Arguments:
            check:
                An error code or check name; see :ref:`error-reference`.
        """
        self._enabled.add(check)

    def set_disabled(self, check: str) -> None:
        """Add a check to the set of disabled checks.

        Arguments:
            check:
                An error code or check name; see :ref:`error-reference`.
        """
        self._disabled.add(check)

    @property
    def enabled(self) -> Set[str]:
        """The set of enabled checks."""
        return self._enabled.copy()

    @property
    def disabled(self) -> Set[str]:
        """The set of disabled checks."""
        return self._disabled.copy()


def semver_parse_tolerant(version: str) -> Optional[semver.VersionInfo]:
    if not version:
        return None

    try:
        return semver.VersionInfo.parse(version)
    except ValueError:
        # Try again with only the first three components.
        # This is due to annoying mismatch between semver
        # and PEP440 for dealing with dev/pre-release
        # suffixes and so on.
        version = ".".join(version.split(".")[:3])
        return semver.VersionInfo.parse(version)


def summarize(ctx, log, new_version):
    LOG.info("")
    LOG.info("---------------------------------------------------------------------")

    if log.max_change_type == ChangeType.NONE:
        LOG.info("No API changes were found")
        return

    if log.max_change_type == ChangeType.MAJOR:
        change_type_str = "Major"
    else:
        change_type_str = "Minor"

    if (
        ctx.new_version_info
        and ctx.old_version_info
        and ctx.new_version_info < ctx.old_version_info
    ):
        LOG.warning(
            "Warning: 'old' version %s appears newer than 'new' version %s",
            ctx.api_old.version,
            ctx.api_new.version,
        )

    if log.max_change_type <= ctx.max_change_allowed:
        LOG.info(
            "%s API changes were found; appropriate for %s",
            change_type_str,
            ctx.upgrade_str,
        )
        return

    LOG.error(
        "%s API changes were found; inappropriate for %s",
        change_type_str,
        ctx.upgrade_str,
    )
    if new_version:
        LOG.error("New version should be equal or greater than %s", new_version)


class Location:
    def __init__(self, differ, sym_old, sym_new):
        self.differ = differ
        self.sym_old = sym_old
        self.sym_new = sym_new
        self.pushed_old = False
        self.pushed_new = False

    def __enter__(self):
        old_file = self.sym_old.display_file
        old_lineno = self.sym_old.lineno
        new_file = self.sym_new.display_file
        new_lineno = self.sym_new.lineno

        if old_file and not old_file.startswith((".", "/")):
            self.differ.location_stack_old.append((old_file, old_lineno))
            self.pushed_old = True

        if new_file and not new_file.startswith((".", "/")):
            self.differ.location_stack_new.append((new_file, new_lineno))
            self.pushed_new = True

    def __exit__(self, *args, **kwargs):
        if self.pushed_old:
            self.differ.location_stack_old.pop()
        if self.pushed_new:
            self.differ.location_stack_new.pop()


class Differ:
    def __init__(self, api_old, api_new, options):
        self.api_old = api_old
        self.api_new = api_new
        self.options = options
        self.diffed_children = set()
        self.location_stack_old = []
        self.location_stack_new = []

    def location(self, sym_old, sym_new):
        return Location(self, sym_old, sym_new)

    @property
    def old_version_info(self):
        return self._version_info(self.api_old)

    @property
    def new_version_info(self):
        return self._version_info(self.api_new)

    @property
    def max_change_allowed(self):
        old_vinfo = self.old_version_info
        new_vinfo = self.new_version_info

        # default applies if any version is unavailable/incomparable
        out = ChangeType.NONE

        if new_vinfo and old_vinfo:
            if new_vinfo.major == 0:
                # Anything goes for versions 0.y.z
                out = ChangeType.MAJOR
            elif new_vinfo.major > old_vinfo.major:
                out = ChangeType.MAJOR
            elif (
                new_vinfo.major == old_vinfo.major and new_vinfo.minor > old_vinfo.minor
            ):
                out = ChangeType.MINOR

        return out

    @property
    def upgrade_str(self) -> str:
        if not self.api_old.version and not self.api_new.version:
            return "unknown versions"

        versions = []
        for api in (self.api_old, self.api_new):
            versions.append(api.version or "<unknown version>")

        return " => ".join(versions)

    def _version_info(self, api):
        try:
            return semver_parse_tolerant(api.version)
        except Exception:
            # not a version we can understand
            LOG.debug("Can't get package version(s)", exc_info=True)

    def diff_root(self):
        self.diffed_children = set()
        with LoggingContext():
            self.diff(self.api_old, self.api_new)

    def diff(self, sym_old, sym_new):
        try:
            with self.location(sym_old, sym_new):
                self.diff_changed_callable(sym_old, sym_new)

                if sym_old.ob.is_callable and sym_new.ob.is_callable:
                    self.diff_signature(sym_old, sym_new)

                if sym_old.object_ref not in self.diffed_children:
                    self.diffed_children.add(sym_old.object_ref)
                    self.diff_children(sym_old, sym_new)
        except StopDiff:
            pass

    def diff_changed_callable(self, sym_old, sym_new):
        if sym_old.ob.is_callable and not sym_new.ob.is_callable:
            self.NoLongerCallable(sym_old, sym_new)
            raise StopDiff

    def diff_signature(self, sym_old, sym_new):
        if sym_old.ob.is_external or sym_new.ob.is_external:
            # TODO: we could still do something here in some cases
            return

        self.diff_var_args(sym_old, sym_new)
        self.diff_named_args(sym_old, sym_new)
        self.diff_positional_args(sym_old, sym_new)

    def diff_var_args(self, sym_old, sym_new):
        sig_old = sym_old.ob.signature
        sig_new = sym_new.ob.signature

        if sig_old.has_var_positional and not sig_new.has_var_positional:
            self.RemovedVarArgs(sym_old, sym_new)
            raise StopDiff

        if sig_old.has_var_keyword and not sig_new.has_var_keyword:
            self.RemovedVarKeywordArgs(sym_old, sym_new)
            raise StopDiff

        if not sig_old.has_var_positional and sig_new.has_var_positional:
            self.AddedVarArgs(sym_old, sym_new)

        if not sig_old.has_var_keyword and sig_new.has_var_keyword:
            self.AddedVarKeywordArgs(sym_old, sym_new)

    def diff_positional_args(self, sym_old, sym_new):
        sig_old = sym_old.ob.signature
        sig_new = sym_new.ob.signature

        old_arg_names = sig_old.positional_args
        new_arg_names = sig_new.positional_args

        for (idx, old_arg) in enumerate(old_arg_names):
            old_arg = old_arg_names[idx]
            if idx >= len(new_arg_names) and sig_new.has_var_positional:
                # OK, this arg can be accepted by the var positional
                continue

            if old_arg not in new_arg_names:
                self.UnpositionalArg(
                    sym_old, sym_new, arg_name=old_arg, old_position=idx
                )
                raise StopDiff

            new_arg_idx = new_arg_names.index(old_arg)
            if idx != new_arg_idx:
                self.MovedArg(
                    sym_old,
                    sym_new,
                    arg_name=old_arg,
                    old_position=idx,
                    new_position=new_arg_idx,
                )
                raise StopDiff

            new_arg = new_arg_names[idx]
            if not sig_old.has_default_for(old_arg) and sig_new.has_default_for(
                new_arg
            ):
                self.AddedArgDefault(sym_old, sym_new, arg_name=old_arg)

    def diff_named_args(self, sym_old, sym_new):
        sig_old = sym_old.ob.signature
        sig_new = sym_new.ob.signature

        old_arg_names = sig_old.named_kwargs
        new_arg_names = sig_new.named_kwargs

        removed_args = ", ".join(sorted(list(old_arg_names - new_arg_names)))
        if removed_args and not sig_new.has_var_keyword:
            self.RemovedArg(sym_old, sym_new, arg_name=removed_args)
            raise StopDiff

        added_args = sorted(list(new_arg_names - old_arg_names))
        added_optional = []
        added_mandatory = []
        for added in added_args:
            if sig_new.has_default_for(added):
                added_optional.append(added)
                continue
            added_mandatory.append(added)

        if added_mandatory:
            self.AddedArg(sym_old, sym_new, arg_name=", ".join(added_mandatory))
            raise StopDiff

        if added_optional:
            self.AddedOptionalArg(sym_old, sym_new, arg_name=", ".join(added_optional))

    def diff_children(self, sym_old, sym_new):
        old_children = sym_old.children_by_name
        new_children = sym_new.children_by_name
        old_child_names = old_children.keys()
        new_child_names = new_children.keys()

        removed_names = old_child_names - new_child_names
        added_names = new_child_names - old_child_names
        common_names = old_child_names & new_child_names

        for name in sorted(list(removed_names)):
            self.removed_child(old_children[name], sym_new)

        for name in sorted(list(added_names)):
            self.added_child(sym_old, new_children[name])

        for name in sorted(list(common_names)):
            self.diff(old_children[name], new_children[name])

    def removed_child(self, child_old, sym_new):
        ob_type = child_old.ob.object_type

        if ob_type == "module" and child_old.ob.is_external:
            fn = self.RemovedExternalModule
        else:
            fns = {
                "function": self.RemovedFunction,
                "module": self.RemovedModule,
                "method": self.RemovedMethod,
                "class": self.RemovedClass,
            }
            fn = fns.get(ob_type, self.RemovedSym)
        return fn(child_old, sym_new)

    def added_child(self, sym_old, child_new):
        ob_type = child_new.ob.object_type

        if ob_type == "module" and child_new.ob.is_external:
            fn = self.AddedExternalModule
        else:
            fns = {
                "function": self.AddedFunction,
                "module": self.AddedModule,
                "method": self.AddedMethod,
                "class": self.AddedClass,
            }
            fn = fns.get(ob_type, self.AddedSym)
        return fn(sym_old, child_new)

    def is_enabled(self, code):
        enabled = self.options.enabled
        disabled = self.options.disabled

        for name in (code.errcode, code.errname):
            if name in enabled:
                return True

        for name in (code.errcode, code.errname):
            if name in disabled:
                return False

        return True

    def __getattr__(self, name):
        code_instance = getattr(Codes, name, None)
        if not code_instance:
            raise AttributeError()

        if self.is_enabled(code_instance):
            return functools.partial(
                code_instance.log,
                old_location=self.location_stack_old[-1],
                new_location=self.location_stack_new[-1],
            )

        return lambda *_args, **_kwargs: None


class DiffResult:
    """The result of a diff."""

    def __init__(
        self,
        max_change_type: ChangeType,
        max_change_allowed: ChangeType,
        proposed_version: str = None,
    ):
        self.max_change_type = max_change_type
        """The most severe :class:`~pidiff.ChangeType` encountered during this
        diff.
        """

        self.max_change_allowed = max_change_allowed
        """The most severe :class:`~pidiff.ChangeType` which should be
        permitted during this diff, according to the version numbers of the
        diffed modules and SemVer.
        """

        self.proposed_version = proposed_version
        """Proposed version number for the new version of the diffed module,
        according to SemVer rules. ``None`` if the version of the old module
        is unknown.

        .. versionadded:: 1.5.0
        """

    @property
    def failed(self) -> bool:
        """True if this diff discovered changes in violation of
        `the SemVer spec <https://semver.org/>`_.
        """
        return self.max_change_type > self.max_change_allowed


def diff(
    api_old: dict, api_new: dict, options: Optional[DiffOptions] = None
) -> DiffResult:
    """Perform a diff between two interfaces.

    Arguments:

        api_old (dump):
            An interface dump as returned by :func:`~pidiff.dump_module`;
            typically, the dump of an old version of an interface would
            be provided.

        api_new (dump):
            A second interface dump.

        options (DiffOptions):
            Options to adjust the behavior of the diff.

    Returns:

        DiffResult:
            Result of the diff.

    **Logging**:

        This function returns only an overall result of a diff.
        If more details are required, the caller should listen for log
        messages sent to the ``pidiff.diff`` logger.

        Records will be streamed to this logger during the diff,
        including fields:

        message:
            Human-oriented message explaining a change
        extra.change_type:
            A :class:`~pidiff.ChangeType` representing the severity of
            this change; or absent, for summary log messages
    """

    options = options or DiffOptions()

    schema.validate(api_old)
    schema.validate(api_new)

    api_old = Symbol.from_root(api_old, options)
    api_new = Symbol.from_root(api_new, options)
    differ = Differ(api_old, api_new, options)

    with CapturedLog() as log:
        differ.diff_root()

    if differ.old_version_info:
        if log.max_change_type == ChangeType.MAJOR:
            new_version = differ.old_version_info.bump_major()
        elif log.max_change_type == ChangeType.MINOR:
            new_version = differ.old_version_info.bump_minor()
        else:
            new_version = differ.old_version_info.bump_patch()

        new_version = str(new_version)
    else:
        new_version = None

    if options.summarize:
        summarize(differ, log, new_version)

    return DiffResult(log.max_change_type, differ.max_change_allowed, new_version)
