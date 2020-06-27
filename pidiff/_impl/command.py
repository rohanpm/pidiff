import os.path
import argparse
import logging
import subprocess
import sys
import glob
import datetime
import re
import hashlib
import json
import shutil
from typing import Union, Optional, NoReturn

from virtualenvapi.manage import VirtualEnvironment
from virtualenvapi.exceptions import PackageInstallationException

import pidiff
from pidiff import diff, DiffOptions, ChangeType

from .schema import validate
from .pipargs import PipArgs
from . import config

LOG = logging.getLogger("pidiff.command")
CACHE_DAYS = 2


class VirtualEnvironmentExt(VirtualEnvironment):
    @property
    def sitepackages_dir(self) -> str:
        return subprocess.check_output(
            [
                os.path.join(self.path, "bin/python"),
                "-c",
                (
                    "import distutils.sysconfig; "
                    "print(distutils.sysconfig.get_python_lib())"
                ),
            ],
            cwd="/",
            encoding="utf-8",
        ).strip()

    def link_self(self, pipargs) -> None:
        # We'll need our own dependencies in the virtualenv too
        self.install_or_die("jsonschema", options=pipargs.excluding_requirements)
        self.install_or_die("astroid", options=pipargs.excluding_requirements)

        sitepackages = self.sitepackages_dir

        for dep_name, dep_module in [("pidiff", pidiff)]:
            src = os.path.dirname(dep_module.__file__)
            dst = os.path.join(sitepackages, dep_name)
            if not os.path.exists(dst):
                os.symlink(src, dst)

    def install_or_die(self, package, *args, **kwargs) -> None:
        all_kwargs = {}
        all_kwargs.update(kwargs)

        if os.path.isfile(os.path.join(package, "setup.py")):
            # If pointing at something locally, install in editable mode.
            # (This is an odd API - install will internally split this
            # before passing to pip)
            package = os.path.abspath(package)
            package = "-e " + package
        try:
            self.install(package, *args, **kwargs)
        except PackageInstallationException:
            # Try to show build log if we can
            try:
                with open(os.path.join(self.path, "build.log")) as log_file:
                    LOG.error("%s", log_file.read())
                with open(os.path.join(self.path, "build.err")) as log_file:
                    LOG.error("%s", log_file.read())
            except Exception:
                LOG.exception(
                    "An exception was encountered while accessing install logs"
                )

            LOG.error("Failed to install: %s", package)
            sys.exit(16)

    def dump(self, root):
        python = os.path.join(self.path, "bin/python")
        command = [python, "-m", "pidiff._impl.dump.command", root]
        output_filename = os.path.join(self.path, "dump.json")

        with open(output_filename, "w") as f:
            subprocess.check_call(command, encoding="utf-8", stdout=f, cwd="/")

        with open(output_filename, "r") as f:
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

    def dist_toplevel(self, name) -> Optional[str]:
        try:
            return subprocess.check_output(
                [
                    os.path.join(self.path, "bin/python"),
                    "-c",
                    (
                        "import pkg_resources;"
                        "import sys;"
                        "x=pkg_resources.get_distribution(sys.argv[1])"
                        '.get_metadata("top_level.txt");'
                        "sys.stdout.write(x)"
                    ),
                    name,
                ],
                cwd="/",
                encoding="utf-8",
            ).strip()
        except subprocess.CalledProcessError:
            LOG.debug("Reading top_level.txt for %s failed", name, exc_info=True)
            return None


def clean_cache(path: str) -> None:
    for basename in glob.glob(os.path.join(path, "*")):
        child_path = os.path.join(path, basename)
        mtime = datetime.datetime.utcfromtimestamp(os.path.getmtime(child_path))
        delta = datetime.datetime.utcnow() - mtime
        if delta.days >= CACHE_DAYS:
            LOG.debug("Clean %s (%s days old)", child_path, delta.days)
            shutil.rmtree(child_path, ignore_errors=True)


def cachedir() -> str:
    cache_home = os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
    out = os.path.join(cache_home, "pidiff")

    try:
        clean_cache(out)
    except OSError:
        LOG.debug("error during clean of %s", out, exc_info=True)

    return out


def cachekey(source: str) -> str:
    m = hashlib.sha1()
    m.update(os.getcwd().encode())
    m.update(source.encode())

    # If source appears to be a local path, mix in any setup.py and requirements.txt
    # into the cache key. This makes the tool reasonably likely to automatically
    # rebuild venv when deps change.  This of course is best-effort since there is
    # no way of knowing exactly how the requirements are generated.

    filenames = [
        os.path.join(source, "setup.py"),
        os.path.join(source, "requirements.txt"),
    ]

    for filename in filenames:
        try:
            with open(filename, "rb") as f:
                m.update(f.read())
            LOG.debug("Used for cache: %s", filename)
        except OSError as exc:
            LOG.debug("open %s: %s", filename, exc)

    return m.hexdigest()


def ensure_exists(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        # Set mtime to now for the sake of cleanup
        os.utime(path)


def make_venv_path(source, args) -> str:
    if args.workdir:
        toplevel = args.workdir
    else:
        toplevel = cachedir()

    out = os.path.join(toplevel, cachekey(source))

    if args.recreate and os.path.exists(out):
        LOG.debug("Clean existing virtualenv %s", out)
        shutil.rmtree(out)

    ensure_exists(out)

    return out


def exitcode_for_result(result):
    if not result.failed:
        return 0

    if result.max_change_type == ChangeType.MAJOR:
        return 99

    return 88


def get_diff_options(args) -> DiffOptions:
    out = DiffOptions()

    if args.full_symbol_names:
        out.full_symbol_names = True

    config.add_checks(args.enable, out.set_enabled)
    config.add_checks(args.disable, out.set_disabled)

    config.adjust_options_from_ini(out)

    return out


def exit_module_unknown() -> NoReturn:
    LOG.error(
        "Top-level module for the given packages could not be determined. "
        "Please pass a module_name argument."
    )
    sys.exit(32)


def get_dist_name(pkg) -> Optional[str]:
    # --editable case
    setup_py = os.path.join(pkg, "setup.py")
    if os.path.exists(setup_py):
        out = subprocess.check_output(
            ["python", setup_py, "--name"], encoding="utf-8"
        ).strip()
        LOG.debug("%s resolves to %s via setup.py", pkg, out)
        return out

    # other case
    # The idea here is to resolve "foo==1.0.0" to "foo"
    # Not sure what's the full set of rules for pip arguments, this is a guess
    matched = re.match(r"[0-9a-zA-Z_\-]+", pkg)
    if matched:
        out = matched.group(0)
        LOG.debug("%s resolves to %s", pkg, out)
        return out

    return None


def detect_module(env1, pkg1, env2, pkg2) -> Union[str, NoReturn]:
    """Figure out and return the top-level name of a module given on the commandline"""
    dist_name = get_dist_name(pkg1)
    if not dist_name:
        dist_name = get_dist_name(pkg2)
    if not dist_name:
        exit_module_unknown()

    toplevel = env1.dist_toplevel(dist_name)
    if not toplevel:
        toplevel = env2.dist_toplevel(dist_name)
    if not toplevel:
        exit_module_unknown()

    lines = toplevel.splitlines()
    if len(lines) == 1:
        LOG.debug("%s top level resolves to %s", dist_name, lines[0])
        return lines[0]

    LOG.debug("top_level.txt for %s:\n%s", dist_name, toplevel)
    exit_module_unknown()


def run_diff(args) -> None:
    pipargs = PipArgs(args)

    s1path = make_venv_path(args.source1, args)
    s2path = make_venv_path(args.source2, args)

    LOG.debug("Creating virtualenv at %s", s1path)
    s1env = VirtualEnvironmentExt(s1path)

    LOG.debug("Creating virtualenv at %s", s2path)
    s2env = VirtualEnvironmentExt(s2path)

    LOG.debug("Installing %s to %s", args.source1, s1path)
    s1env.install_or_die(args.source1, upgrade=True, options=pipargs.all)

    LOG.debug("Installing %s to %s", args.source2, s2path)
    s2env.install_or_die(args.source2, upgrade=True, options=pipargs.all)

    module_name = args.module_name
    if not module_name:
        module_name = detect_module(s1env, args.source1, s2env, args.source2)

    s1env.link_self(pipargs)
    s2env.link_self(pipargs)

    s1api = s1env.dump_or_exit(module_name, args.source1)
    s2api = s2env.dump_or_exit(module_name, args.source2)

    result = diff(s1api, s2api, get_diff_options(args))

    if args.gen_version:
        if not result.proposed_version:
            LOG.error("Unable to determine new version!")
            sys.exit(30)

        print(result.proposed_version)
        sys.exit(0)
    else:
        sys.exit(exitcode_for_result(result))


def argparser():
    parser = argparse.ArgumentParser(
        description=(
            "Check for differences between two versions of a Python API, "
            "and complain if SemVer is not followed."
        )
    )

    parser.add_argument("--workdir", help="Use this working directory")

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose execution"
    )

    parser.add_argument(
        "--full-symbol-names",
        action="store_true",
        help="Use fully qualified names in log messages",
    )

    parser.add_argument(
        "-r",
        "--recreate",
        action="store_true",
        help="Force recreation of virtual environments",
    )

    parser.add_argument(
        "--gen-version",
        action="store_true",
        help=(
            "Version generator mode: report is written to stderr; "
            "proposed new version number is written to stdout; exit code is 0 "
            "unless an error occurs."
        ),
    )

    parser.add_argument(
        "-e",
        "--enable",
        action="append",
        help=(
            "Enable checks by error code or name. Multiple "
            "checks can be provided, comma-separated. Option "
            "may be provided multiple times."
        ),
    )

    parser.add_argument(
        "-d", "--disable", action="append", help="Disable checks by error code or name."
    )

    parser.add_argument(
        "source1",
        help=(
            "Old package for test; a requirement specifier "
            "as accepted by the pip command"
        ),
    )

    parser.add_argument("source2", help="New package for test")

    parser.add_argument(
        "module_name",
        nargs="?",
        help=(
            "Name of the Python module which serves as the "
            "entry point of the API to test. If omitted, "
            "the command will attempt to determine this automatically "
            "using egg metadata"
        ),
    )

    pip = parser.add_argument_group(
        "pip arguments",
        "These arguments affect the behavior of ``pip install`` while pidiff "
        "installs the packages to be diffed. See ``pip install --help`` "
        "for more info on the behavior of these arguments.",
    )

    pip.add_argument(
        "--requirement",
        action="append",
        help="Install from the given requirements file.",
    )
    pip.add_argument(
        "--constraint",
        "-c",
        action="append",
        help="Constrain versions using the given constraints file.",
    )
    pip.add_argument(
        "--pre",
        action="store_true",
        help="Include pre-release and development versions.",
    )

    pip.add_argument("--index-url", "-i", help="Base URL of the Python Package Index.")
    pip.add_argument(
        "--extra-index-url", action="append", help="Extra URLs of package indexes."
    )

    pip.add_argument(
        "--pip-args", help="Additional arguments to pass to the `pip' command."
    )

    return parser


def main() -> None:
    parser = argparser()

    p = parser.parse_args()

    stream = sys.stderr if p.gen_version else sys.stdout

    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=stream)
    LOG.setLevel(logging.DEBUG if p.verbose else logging.INFO)

    return run_diff(p)
