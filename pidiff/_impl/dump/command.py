import sys
import json

from .dump import dump_module

EXIT_NO_MODULE = 32


def main():
    # Entry point for internal use only
    root_name = sys.argv[1]

    try:
        out = dump_module(root_name)
        json.dump(out, sys.stdout, indent=2)
    except ModuleNotFoundError as error:
        print(error, file=sys.stderr)
        sys.exit(EXIT_NO_MODULE)


if __name__ == "__main__":
    main()  # pragma: no cover
