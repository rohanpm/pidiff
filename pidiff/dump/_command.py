import sys
import json

from ._dump import dump_module

EXIT_NO_MODULE = 32


if __name__ == '__main__':
    # Entry point for internal use only
    root_name = sys.argv[1]

    try:
        out = dump_module(root_name)
        json.dump(out, sys.stdout, indent=2)
    except ModuleNotFoundError as error:
        print(error, file=sys.stderr)
        sys.exit(EXIT_NO_MODULE)
