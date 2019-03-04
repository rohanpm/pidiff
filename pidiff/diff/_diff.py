import logging

from .. import _schema as schema
from ._codes import Codes
from ._api import Api


LOG = logging.getLogger('pidiff')


class StopDiff(Exception):
    """This exception is thrown when diffing of a particular
    symbol should be stopped, e.g. because differences already
    covered make further testing irrelevant.
    """


def diff(api_old, api_new):
    schema.validate(api_old)
    schema.validate(api_new)
    _diff(Api(api_old), Api(api_new), toplevel=True)


def _diff_changed_callable(sym_old, sym_new):
    if sym_old.is_callable and not sym_new.is_callable:
        Codes.NoLongerCallable.log(sym_old, sym_new)
        raise StopDiff


def _diff_signature(sym_old, sym_new):
    if sym_old.is_external or sym_new.is_external:
        return
    sig_old = sym_old.signature
    sig_new = sym_new.signature
    old_arg_names = sig_old.named_kwargs
    new_arg_names = sig_new.named_kwargs

    removed_args = ','.join(sorted(list(old_arg_names - new_arg_names)))
    if removed_args and not sig_new.has_var_keyword:
        Codes.RemovedArg.log(sym_old, sym_new, arg_name=removed_args)
        raise StopDiff


def _diff(sym_old, sym_new, toplevel=False):
    try:
        if not toplevel:
            _diff_changed_callable(sym_old, sym_new)

        if sym_old.is_callable and sym_new.is_callable:
            _diff_signature(sym_old, sym_new)

        _diff_children(sym_old, sym_new)
    except StopDiff:
        pass


def _diff_children(sym_old, sym_new):
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
        _diff(old_children[name], new_children[name])
