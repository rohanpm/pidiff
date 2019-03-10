import logging

import semver  # type: ignore

from .. import _schema as schema
from ._codes import Codes, ChangeType
from ._api import Symbol


LOG = logging.getLogger('pidiff')


class StopDiff(Exception):
    """This exception is thrown when diffing of a particular
    symbol should be stopped, e.g. because differences already
    covered make further testing irrelevant.
    """


class Interceptor(logging.NullHandler):
    def __init__(self):
        super().__init__()
        self.max_change_type = None

    def handle(self, record):
        change_type = getattr(record, 'change_type', None)
        if self.max_change_type is None:
            self.max_change_type = change_type
        elif change_type is not None:
            self.max_change_type = max(change_type, self.max_change_type)


class CapturedLog:
    def __init__(self):
        self._handler = None

    def __enter__(self):
        self._handler = Interceptor()
        logging.getLogger('pidiff.diff').addHandler(self._handler)
        return self

    def __exit__(self, *args, **kwargs):
        assert self._handler
        logging.getLogger('pidiff.diff').removeHandler(self._handler)

    @property
    def max_change_type(self):
        return self._handler.max_change_type


def semver_parse_tolerant(version: str):
    if not version:
        return None

    try:
        return semver.parse_version_info(version)
    except ValueError:
        # Try again with only the first three components.
        # This is due to annoying mismatch between semver
        # and PEP440 for dealing with dev/pre-release
        # suffixes and so on.
        version = '.'.join(version.split('.')[:3])
        return semver.parse_version_info(version)


def summarize(ctx, log):
    LOG.info("\n---------------------------------------------------------------------")

    if log.max_change_type is None:
        LOG.info("No API changes were found")
        return

    if log.max_change_type == ChangeType.INFO:
        LOG.info("No minor or major API changes were found")
        return

    if log.max_change_type == ChangeType.MAJOR:
        change_type_str = 'Major'
        bump_version = semver.bump_major
    else:
        change_type_str = 'Minor'
        bump_version = semver.bump_minor

    if ctx.new_version_info and ctx.old_version_info \
            and ctx.new_version_info < ctx.old_version_info:
        LOG.warning("Warning: 'old' version %s appears newer than 'new' version %s",
                    ctx.api_old.version, ctx.api_new.version)

    if log.max_change_type <= ctx.max_change_allowed:
        LOG.info("%s API changes were found; appropriate for %s", change_type_str, ctx.upgrade_str)
        return

    LOG.error("%s API changes were found; inappropriate for %s", change_type_str, ctx.upgrade_str)
    if ctx.old_version_info:
        LOG.error("New version should be equal or greater than %s",
                  bump_version(str(ctx.old_version_info)))


class Differ:
    def __init__(self, api_old, api_new):
        self.api_old = api_old
        self.api_new = api_new
        self.diffed_children = set()

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
        out = ChangeType.INFO

        if new_vinfo and old_vinfo:
            if new_vinfo.major > old_vinfo.major:
                out = ChangeType.MAJOR
            elif new_vinfo.major == old_vinfo.major and new_vinfo.minor > old_vinfo.minor:
                out = ChangeType.MINOR

        return out

    @property
    def upgrade_str(self) -> str:
        if not self.api_old.version and not self.api_new.version:
            return 'unknown versions'

        versions = []
        for api in (self.api_old, self.api_new):
            versions.append(api.version or '<unknown version>')

        return ' => '.join(versions)

    def _version_info(self, api):
        try:
            return semver_parse_tolerant(api.version)
        except Exception:
            # not a version we can understand
            LOG.debug("Can't get package version(s)", exc_info=True)

    def diff_root(self):
        self.diffed_children = set()
        self.diff(self.api_old, self.api_new)

    def diff(self, sym_old, sym_new):
        try:
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
            Codes.NoLongerCallable.log(sym_old, sym_new)
            raise StopDiff

    def diff_signature(self, sym_old, sym_new):
        if sym_old.ob.is_external or sym_new.ob.is_external:
            return
        sig_old = sym_old.ob.signature
        sig_new = sym_new.ob.signature
        old_arg_names = sig_old.named_kwargs
        new_arg_names = sig_new.named_kwargs

        removed_args = ', '.join(sorted(list(old_arg_names - new_arg_names)))
        if removed_args and not sig_new.has_var_keyword:
            Codes.RemovedArg.log(sym_old, sym_new, arg_name=removed_args)
            raise StopDiff

    def diff_children(self, sym_old, sym_new):
        old_children = sym_old.children_by_name
        new_children = sym_new.children_by_name
        old_child_names = old_children.keys()
        new_child_names = new_children.keys()

        removed_names = old_child_names - new_child_names
        added_names = new_child_names - old_child_names
        common_names = old_child_names & new_child_names

        for name in sorted(list(removed_names)):
            Codes.RemovedSym.log(old_children[name], sym_new)

        for name in sorted(list(added_names)):
            Codes.AddedSym.log(sym_old, new_children[name])

        for name in sorted(list(common_names)):
            self.diff(old_children[name], new_children[name])


def diff(api_old, api_new):
    schema.validate(api_old)
    schema.validate(api_new)

    api_old = Symbol.from_root(api_old)
    api_new = Symbol.from_root(api_new)
    differ = Differ(api_old, api_new)

    with CapturedLog() as log:
        differ.diff_root()

    summarize(differ, log)
