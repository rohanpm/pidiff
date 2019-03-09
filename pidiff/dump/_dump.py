import argparse
import importlib
import inspect
import logging
from typing import Optional, Any, Dict
import os.path
import pkg_resources

from .. import _schema as schema


Dump = Dict[str, Any]


LOG = logging.getLogger('pidiff')


def is_public(name) -> bool:
    if name in [
            '__new__',
            '__init__',
            '__del__',
            '__getitem__',
            '__repr__',
            '__str__',
            '__bytes__',
            '__format__',
            '__lt__',
            '__le__',
            '__eq__',
            '__ne__',
            '__gt__',
            '__ge__',
            '__hash__',
            '__bool__',
            '__getattr__',
            '__getattribute__',
            '__setattr__',
            '__delattr__',
            '__dir__',
    ]:
        return True
    return not name.startswith('_')


def get_file(value) -> Optional[str]:
    try:
        return inspect.getsourcefile(value)
    except TypeError:
        pass
    try:
        return value.__file__
    except Exception:
        pass
    try:
        module = importlib.import_module(value.__module__)
        return module.__file__
    except Exception:
        pass
    return None


def dump_signature(out, subject) -> None:
    sig = inspect.signature(subject)

    for param in sig.parameters.values():
        elem: Dump = {}
        elem['name'] = param.name
        elem['has_default'] = (param.default is not param.empty)
        elem['kind'] = str(param.kind)
        out.append(elem)


def get_symbol_type(value) -> str:
    class Klass:
        pass

    if isinstance(value, type(lambda: None)):
        return 'function'

    if isinstance(value, type(Klass)):
        return 'class'

    if isinstance(value, type(argparse)):
        return 'module'

    return 'object'


def set_location(out, subject) -> None:
    subject_file = get_file(subject)

    if subject_file:
        out['file'] = subject_file
        try:
            (_, lineno) = inspect.getsourcelines(subject)
            if lineno is not None:
                out['lineno'] = lineno
        except OSError:
            pass
        except TypeError:
            pass


def dump_interface(out, name, subject, include_dirs, seen=None):
    if seen is None:
        seen = set()

    out['name'] = name
    out['symbol_type'] = get_symbol_type(subject)
    out['is_callable'] = callable(subject)

    set_location(out, subject)

    if not out.get('file') or not out.get('file').startswith(include_dirs + '/'):
        out['is_external'] = True
        return

    out['is_external'] = False

    if out['is_callable']:
        dump_signature(out.setdefault('signature', []), subject)

    # Don't bother to look at children of magic methods
    # since the methods are not to be accessed directly
    if name.startswith('__') and out['is_callable']:
        return

    if id(subject) in seen:
        # TODO: make some kind of ref here?
        return

    seen = seen | set([id(subject)])

    child_names = [attr for attr in dir(subject) if is_public(attr)]

    for child_name in child_names:
        try:
            child = getattr(subject, child_name)
        except Exception:
            LOG.debug("Can't getattr %s %s", subject, child_name, exc_info=True)
            continue

        child_out = {}
        dump_interface(child_out, child_name, child, include_dirs, seen)
        out.setdefault('children', []).append(child_out)


def import_recurse(module_name: str):
    module = importlib.import_module(module_name)

    module_all = getattr(module, '__all__', [])
    for submodule in module_all:
        try:
            import_recurse('.'.join([module_name, submodule]))
        except ModuleNotFoundError:
            pass

    return module


def egg_for_root(root_name: str):
    # FIXME: why are both mypy and pylint getting things wrong here
    # for pkg_resources? Something wrong with the setup?
    for dist in pkg_resources.working_set:  # pylint: disable=not-an-iterable
        egg_info = dist.egg_info  # type: ignore
        if not egg_info:
            continue
        try:
            with open(os.path.join(egg_info, 'top_level.txt')) as f:
                lines = [line.strip() for line in f.readlines()]
                if root_name in lines:
                    return dist
        except OSError:
            LOG.debug("Can't check %s", egg_info, exc_info=True)


def dump_version(out: Dump, root_name: str, module) -> None:
    # PEP 396
    from_module = getattr(module, '__version__', None)
    if from_module:
        out['version'] = from_module
        return

    # OK then, try to find a relevant egg
    egg = egg_for_root(root_name)
    if egg:
        out['version'] = egg.version


def dump_module(root_name: str) -> Dump:
    out: Dump = {}
    module = import_recurse(root_name)
    module_dir = os.path.dirname(module.__file__)

    # We only look at top-level versions
    dump_version(out, root_name, module)
    dump_interface(out, root_name, module, include_dirs=module_dir)

    schema.validate(out)

    return out
