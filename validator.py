"""Row validation: airport list loading, single-row checks, record building."""

# I asked Claude whether I needed to import libraries, and it suggested these.
# I also asked it to check whether they were allowed by the assignment. Here is its answer:
# "Yes, you can add them. The instructions forbid third-party libraries, meaning those
# installed with pip like pandas. They require the standard library, the one shipped
# with Python. math and datetime are part of it, like csv, json, logging, argparse and re."
import math
from datetime import datetime


# I asked if I needed other functions, and the AI suggested creating
# _has_datetime_format and _is_valid_datetime. I completed the body of these functions.
def _has_datetime_format(text):
    if len(text) != 16:
        return False
    for i in range(16):
        ch = text[i]
        if i == 4 or i == 7:
            if ch != "-":
                return False
        elif i == 10:
            if ch != " ":
                return False
        elif i == 13:
            if ch != ":":
                return False
        else:
            if not ("0" <= ch <= "9"):
                return False
    return True


def _is_valid_datetime(text):
    if not _has_datetime_format(text):
        return False
    try:
        # asked to the AI: datetime.strptime(text, format) raises a ValueError if the
        # date does not really exist (month 13, February 30, hour 24...)
        datetime.strptime(text, "%Y-%m-%d %H:%M")
    except ValueError:
        return False
    return True


# I tried to run the code but some functions were missing, so the AI told me to
# add them (it only gave me the structure and I completed the bodies):
def _is_ascii_letters_digits(text):
    # Go through each character of text
    for ch in text:
        # If ch is not a letter a-z, not a letter A-Z and not a digit 0-9 -> False
        if not ("a" <= ch <= "z" or "A" <= ch <= "Z" or "0" <= ch <= "9"):
            return False
    return True


def _is_airport_code(code, airports):
    # An airport code has exactly 3 characters
    if len(code) != 3:
        return False
    # Each character must be an uppercase letter A-Z
    for ch in code:
        if not ("A" <= ch <= "Z"):
            return False
    # Finally, the code must exist in the airport list
    return code in airports


def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes.

    One code per line. Strip whitespace; skip blank lines and lines
    starting with '#'.
    """
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f]
    return {line for line in lines if line != "" and line[0] != "#"}


# Here is the prompt I used: "Without writing any code, give me the structure of
# validate_row: 'Split validate_row into small helper functions and tell me which
# one to write first.' 'Give me a skeleton with only the ifs and # TODO comments,
# I will fill in the conditions myself.'"
def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row (fields as returned by csv.reader, not yet stripped).

    Return None if the row is valid, otherwise the error code of the
    FIRST failing check (checks 1-11 in the specification, in order).
    Does not check for duplicates.
    """
    # 1. The number of fields must be exactly 6
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    # Clean the fields (strip) into a new list called values
    values = [field.strip() for field in fields]

    # 2. No field may be empty after cleaning
    for v in values:
        if v == "":
            return "MISSING_FIELD"

    # Give a name to each value
    flight_id, origin, destination, departure, arrival, price = values

    # 3. flight_id: between 2 and 8 characters, only ASCII letters/digits
    if not (2 <= len(flight_id) <= 8 and _is_ascii_letters_digits(flight_id)):
        return "INVALID_FLIGHT_ID"

    # 4. origin: valid airport code
    if not _is_airport_code(origin, airports):
        return "INVALID_ORIGIN"

    # 5. destination: valid airport code
    if not _is_airport_code(destination, airports):
        return "INVALID_DESTINATION"

    # 6. origin and destination must be different
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    # 7. departure must be a real date/time in the exact format
    if not _is_valid_datetime(departure):
        return "INVALID_DEPARTURE"

    # 8. arrival must be a real date/time in the exact format
    if not _is_valid_datetime(arrival):
        return "INVALID_ARRIVAL"

    # 9. arrival must be after departure (same format, so text comparison works)
    if arrival <= departure:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    # 10. price must be a finite number
    try:
        price_value = float(price)
    except ValueError:
        return "INVALID_PRICE"
    # asked to the AI: math.isfinite(x) is False for nan, inf and -inf
    if not math.isfinite(price_value):
        return "INVALID_PRICE"

    # 11. price must be strictly positive
    if price_value <= 0:
        return "NON_POSITIVE_PRICE"

    return None


# I asked: "ok, give me the skeleton of to_record so that I can complete it myself please".
# The AI gave the skeleton and I added the body.
def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary.

    Keys: flight_id, origin, destination, departure_datetime,
    arrival_datetime (stripped strings) and price (float).
    """
    # 1. Clean the 6 fields: remove the spaces at the start and end of each one
    values = [field.strip() for field in fields]

    # 2. Build the dictionary with the 6 exact keys of the assignment
    record = {
        "flight_id": values[0],
        "origin": values[1],
        "destination": values[2],
        "departure_datetime": values[3],
        "arrival_datetime": values[4],
        "price": float(values[5]),   # careful: this must be a number, not a string
    }

    # 3. Return the dictionary
    return record