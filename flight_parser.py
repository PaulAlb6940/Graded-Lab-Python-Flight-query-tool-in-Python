"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""

# Here the AI helped me, but I wrote more of the structure than usual, and the
# body as well; the AI guided me less in the skeleton.

import argparse
import json
import logging
import os
import sys
from datetime import datetime

from validator import load_airports
from csv_loader import parse_files
from query import run_queries

# Student details: plain ASCII, no spaces or underscores.
STUDENT_ID = "260ADB178"
FIRST_NAME = "Paul"
LAST_NAME = "Alberti"


def _build_parser():
    # asked to the AI: argparse (required by the assignment)
    parser = argparse.ArgumentParser(description="Flight schedule parser and query tool")
    # exactly one source among -i / -d / -j (otherwise argparse exits with code 2)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", metavar="FILE", help="parse a single CSV file")
    source.add_argument("-d", metavar="FOLDER", help="parse all .csv files in a folder")
    source.add_argument("-j", metavar="FILE", help="load an existing JSON database")
    parser.add_argument("-a", metavar="FILE", help="airport list (required with -i/-d)")
    parser.add_argument("-o", metavar="FILE", help="output JSON database (default: db.json)")
    parser.add_argument("-q", metavar="FILE", help="JSON file with queries")
    parser.add_argument("-r", metavar="FOLDER", default=".", help="folder for the response file")
    return parser


def _list_csv_files(folder):
    # asked to the AI: the skeleton, and os.listdir (names in the folder),
    # os.path.join, os.path.isfile
    paths = []
    names = os.listdir(folder)
    names.sort()   # alphabetical order (list method, course 9)
    for name in names:
        path = os.path.join(folder, name)
        # keep only the files whose name ends with ".csv" (no sub-folders)
        if name[-4:] == ".csv" and os.path.isfile(path):
            paths.append(path)
    return paths


def _load_json(path):
    # open the file for reading (utf-8) and return json.load(...)  -> course 10
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(argv: list[str] | None = None) -> int:
    # 1. argv = None -> take the command-line arguments
    if argv is None:
        argv = sys.argv[1:]

    # 2. Read the arguments. argparse calls sys.exit on a usage error:
    # we catch SystemExit to RETURN the code (0 for -h, 2 otherwise)
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
        # -a is required with -i or -d
        if (args.i is not None or args.d is not None) and args.a is None:
            parser.error("-a is required with -i or -d")
        # -o is forbidden with -j
        if args.j is not None and args.o is not None:
            parser.error("-o cannot be used with -j")
    except SystemExit as e:
        return e.code

    logger = logging.getLogger("flight_parser")
    handler = None
    try:
        if args.j is not None:
            # 3a. -j mode: load the database, which must be a list of dictionaries
            # asked to the AI: isinstance(x, type) checks the type of a value,
            # and raise ValueError(...) triggers an error caught below
            db = _load_json(args.j)
            if not isinstance(db, list):
                raise ValueError("database must be a JSON array")
            for item in db:
                if not isinstance(item, dict):
                    raise ValueError("database must contain only objects")
        else:
            # 3b. -i / -d mode: list of the CSV paths
            if args.i is not None:
                paths = [args.i]
            else:
                paths = _list_csv_files(args.d)
                if len(paths) == 0:   # no .csv found
                    raise ValueError("no .csv files in folder " + args.d)

            airports = load_airports(args.a)

            # database path: -o if given, otherwise "db.json"
            if args.o is not None:
                db_path = args.o
            else:
                db_path = "db.json"
            # errors.log in the same folder as the database (asked to the AI: os.path.dirname)
            log_path = os.path.join(os.path.dirname(db_path), "errors.log")

            # configuration required by the assignment
            logger.setLevel(logging.INFO)
            handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
            logger.addHandler(handler)

            db, errors = parse_files(paths, airports)
            # one WARNING per error message, in order
            for message in errors:
                logger.warning(message)
            # write db into db_path with json.dump (course 10, slide 12)
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(db, f)

        # 4. Queries (-q): an object or a list, otherwise error
        if args.q is not None:
            queries = _load_json(args.q)
            if not isinstance(queries, (dict, list)):
                raise ValueError("queries must be a JSON object or array")
            responses = run_queries(db, queries)
            # asked to the AI: datetime.now().strftime -> local time "YYYYMMDD_HHMM"
            stamp = datetime.now().strftime("%Y%m%d_%H%M")
            name = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{stamp}.json"
            # write responses into os.path.join(args.r, name) with json.dump
            with open(os.path.join(args.r, name), "w", encoding="utf-8") as f:
                json.dump(responses, f)

        return 0

    except (OSError, ValueError) as e:
        # file not found / unreadable, invalid JSON, wrong structure -> code 1
        # asked to the AI: file=sys.stderr writes to the error output
        print(f"Error: {e}", file=sys.stderr)
        return 1

    finally:
        # ALWAYS remove and close the handler, even after an error
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()


if __name__ == "__main__":
    sys.exit(main())