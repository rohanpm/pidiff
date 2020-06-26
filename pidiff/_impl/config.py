import configparser
import os
import re

CANDIDATES = ["pidiff.ini", "tox.ini", "setup.cfg"]


def read_config():
    path = os.getcwd()
    parser = configparser.ConfigParser(strict=False, allow_no_value=True)

    while path != "/":
        filenames = [os.path.join(path, basename) for basename in CANDIDATES]
        for filename in filenames:
            parser.read([filename])
            if parser.has_section("pidiff"):
                return parser
        path = os.path.dirname(path)

    return parser


def add_checks(arg_values, option_method):
    for arg_value in arg_values or []:
        for check in re.split(r"[,\n ]+", arg_value or ""):
            check = check.strip()
            if check:
                option_method(check)


def adjust_options_from_ini(options):
    config = read_config()

    enable = config.get("pidiff", "enable", fallback=None)
    disable = config.get("pidiff", "disable", fallback=None)

    add_checks([enable], options.set_enabled)
    add_checks([disable], options.set_disabled)
