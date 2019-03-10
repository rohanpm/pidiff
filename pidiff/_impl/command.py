import os.path
import argparse
import logging
import subprocess
import sys
import json
import shutil
from typing import Union
from tempfile import TemporaryDirectory

from virtualenvapi.manage import VirtualEnvironment
from virtualenvapi.exceptions import PackageInstallationException

import pidiff
from pidiff import diff, DiffOptions, ChangeType

from .schema import validate

LOG = logging.getLogger('pidiff.command')


class Directory:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass


AnyDirectory = Union[TemporaryDirectory, Directory]


class VirtualEnvironmentExt(VirtualEnvironment):
    @property
    def sitepackages_dir(self) -> str:
        return subprocess.check_output([
            os.path.join(self.path, 'bin/python'),
            '-c',
            ('import distutils.sysconfig; '
             'print(distutils.sysconfig.get_python_lib())')
        ], cwd='/', encoding='utf-8').strip()

    def link_self(self) -> None:
        # We'll need our own dependencies in the virtualenv too
        self.install_or_die('jsonschema')

        sitepackages = self.sitepackages_dir

        for dep_name, dep_module in [
                ('pidiff', pidiff),
        ]:
            src = os.path.dirname(dep_module.__file__)
            dst = os.path.join(sitepackages, dep_name)
            if not os.path.exists(dst):
                os.symlink(src, dst)

    def install_or_die(self, package, *args, **kwargs) -> None:
        all_kwargs = {}
        all_kwargs.update(kwargs)

        if os.path.isdir(package):
            # If pointing at something locally, install in editable mode.
            # (This is an odd API - install will internally split this
            # before passing to pip)
            package = os.path.abspath(package)
            package = '-e ' + package
        try:
            self.install(package, *args, **kwargs)
        except PackageInstallationException:
            # Try to show build log if we can
            try:
                with open(os.path.join(self.path, 'build.log')) as log_file:
                    LOG.error("%s", log_file.read())
                with open(os.path.join(self.path, 'build.err')) as log_file:
                    LOG.error("%s", log_file.read())
            except Exception:
                LOG.exception("An exception was encountered while accessing install logs")

            LOG.error("Failed to install: %s", package)
            sys.exit(16)

    def dump(self, root):
        python = os.path.join(self.path, 'bin/python')
        command = [python, '-m', 'pidiff._impl.dump.command', root]
        output_filename = os.path.join(self.path, 'dump.json')

        with open(output_filename, 'w') as f:
            subprocess.check_call(command, encoding='utf-8', stdout=f, cwd='/')

        with open(output_filename, 'r') as f:
            dumped = json.load(f)

        validate(dumped)
        return dumped

    def dump_or_exit(self, root, sourcename):
        LOG.debug("Inspecting API for %s", sourcename)
        try:
            return self.dump(root)
        except subprocess.CalledProcessError:
            LOG.error("Failed to inspect module %s for %s", root, sourcename)
            sys.exit(64)


def make_workdir(requested) -> Union[TemporaryDirectory, Directory]:
    if requested:
        out: Union[TemporaryDirectory, Directory] = Directory(requested)
    elif os.path.exists('.git') or os.path.exists('.tox'):
        out = Directory('.pidiff')
    else:
        out = TemporaryDirectory(prefix='pidiff')
    if not os.path.exists(out.name):
        os.makedirs(out.name)
    return out


def exitcode_for_result(result):
    if not result.failed:
        return 0

    if result.max_change_type == ChangeType.MAJOR:
        return 99

    return 88


def options_from_args(args) -> DiffOptions:
    out = DiffOptions()

    if args.full_symbol_names:
        out.full_symbol_names = True

    return out


def run_diff(args) -> None:
    with make_workdir(args.workdir) as workdir:
        s1path = os.path.join(workdir.name, 's1')
        s2path = os.path.join(workdir.name, 's2')

        if args.recreate:
            for path in (s1path, s2path):
                if os.path.exists(path):
                    LOG.debug("Removing %s", path)
                    shutil.rmtree(path)

        LOG.debug("Creating virtualenvs under %s", workdir.name)
        s1env = VirtualEnvironmentExt(s1path)
        s2env = VirtualEnvironmentExt(s2path)

        LOG.debug("Installing %s to %s", args.source1, s1path)
        s1env.install_or_die(args.source1, upgrade=True)

        LOG.debug("Installing %s to %s", args.source2, s2path)
        s2env.install_or_die(args.source2, upgrade=True)

        s1env.link_self()
        s2env.link_self()

        s1api = s1env.dump_or_exit(args.module_name, args.source1)
        s2api = s2env.dump_or_exit(args.module_name, args.source2)

        result = diff(s1api, s2api, options_from_args(args))
        sys.exit(exitcode_for_result(result))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--workdir',
                        help="Use this working directory")
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='verbose execution')
    parser.add_argument('--full-symbol-names',
                        action='store_true',
                        help='use fully qualified names in log messages')
    parser.add_argument('-r', '--recreate',
                        action='store_true',
                        help='force recreation of virtual environments')
    parser.add_argument('source1')
    parser.add_argument('source2')
    parser.add_argument('module_name')

    p = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(message)s')
    LOG.setLevel(logging.DEBUG if p.verbose else logging.INFO)

    return run_diff(p)
