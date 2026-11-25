"""Reading CSV files into flight records and error messages."""

import csv
import os   #asked to the AI: only used for os.path.basename

from validator import validate_row, to_record

#As described in AI_USAGE.md: I asked the AI for the skeleton (the structure
#to complete), and then I wrote the rest of the code myself.


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
      records - valid flight records, in input order
      errors  - one message per invalid row, in input order, formatted as
                "<file name>:<line number>: <ERROR_CODE> | <free text>"
                (base file name only, no timestamp or level, no newline)

    Also performs the DUPLICATE_FLIGHT check across all the files.
    Does not write any files and does not log anything itself.
    """
    records = []
    errors = []
    seen = set()   #(flight_id, departure_datetime) pairs of the VALID rows already seen

    for path in paths:
        #asked to the AI: os.path.basename("data/db.csv") returns "db.csv"
        filename = os.path.basename(path)

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for number, line in enumerate(lines, start=1):
            #1. Line 1 = header -> go to the next line
            #(the AI's skeleton explained what to do here; I wrote the if ...: continue myself)
            if number == 1:
                continue

            #2. Empty line / only spaces, or comment line
            text = line.strip()
            if text == "" or text[0] == "#":
                continue

            #3. Remove only the final "\n" (for the error message)
            line = line.replace("\n", "")

            #4. Split the line with the csv module
            fields = list(csv.reader([line]))[0]

            #5. Checks 1 to 11
            code = validate_row(fields, airports)

            #6. If valid: build the record + check for a duplicate
            if code is None:
                record = to_record(fields)
                key = (record["flight_id"], record["departure_datetime"])
                if key in seen:
                    code = "DUPLICATE_FLIGHT"
                else:
                    seen.add(key)
                    records.append(record)

            #7. If invalid: add the message to errors
            if code is not None:
                errors.append(
                    filename + ":" + str(number) + ": " + code + " | " + line.strip()
                )

    return records, errors