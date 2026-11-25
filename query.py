"""Running queries against the flight database."""

#Same approach as before: the AI helped me with the structure, and some of
#its guidance is still visible in the comments below.

from validator import _is_valid_datetime

RECORD_KEYS = ["flight_id", "origin", "destination",
               "departure_datetime", "arrival_datetime", "price"]
QUERY_KEYS = RECORD_KEYS + ["min_price", "sort_by", "order", "limit"]


def _is_number(value):
    """True if value is an int or a float, but NOT a bool."""
    #AI skeleton hint: exclude bool first, then check int or float (I wrote the code myself).
    #asked to the AI: isinstance(x, type) checks the type of a value; bool must be
    #excluded first because in Python True/False are also considered ints
    if isinstance(value, bool):
        return False
    return isinstance(value, (int, float))


def _is_valid_query(query):
    """True if the query is valid, False otherwise."""
    #1. Not a dict -> invalid
    if not isinstance(query, dict):
        return False

    #2. Unknown key (e.g. "colour") -> invalid
    for key in query:
        if key not in QUERY_KEYS:
            return False

    #3. flight_id, origin, destination: if present, they must be str
    for key in ("flight_id", "origin", "destination"):
        if key in query and not isinstance(query[key], str):
            return False

    #4. departure_datetime, arrival_datetime: if present, str AND _is_valid_datetime
    for key in ("departure_datetime", "arrival_datetime"):
        if key in query:
            if not isinstance(query[key], str) or not _is_valid_datetime(query[key]):
                return False

    #5. price, min_price: if present, _is_number
    for key in ("price", "min_price"):
        if key in query and not _is_number(query[key]):
            return False

    #6. limit: if present, int (not bool) and >= 0
    if "limit" in query:
        limit = query["limit"]
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
            return False

    #7. sort_by: if present, str AND in RECORD_KEYS
    if "sort_by" in query:
        if not isinstance(query["sort_by"], str) or query["sort_by"] not in RECORD_KEYS:
            return False

    #8. order: if present, "sort_by" must be in the query AND the value must be "asc" or "desc"
    if "order" in query:
        if "sort_by" not in query or query["order"] not in ("asc", "desc"):
            return False

    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    #1. Invalid query -> error entry (we do NOT stop the program)
    if not _is_valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    #2. Filter: a flight is kept only if it meets ALL the conditions (AND)
    matches = []
    for flight in db:
        if "flight_id" in query and flight["flight_id"] != query["flight_id"]:
            continue
        if "origin" in query and flight["origin"] != query["origin"]:
            continue
        if "destination" in query and flight["destination"] != query["destination"]:
            continue
        #dates in the format YYYY-MM-DD HH:MM compare correctly as text
        if "departure_datetime" in query and flight["departure_datetime"] < query["departure_datetime"]:
            continue
        if "arrival_datetime" in query and flight["arrival_datetime"] > query["arrival_datetime"]:
            continue
        if "price" in query and flight["price"] > query["price"]:
            continue
        if "min_price" in query and flight["price"] < query["min_price"]:
            continue
        matches.append(flight)

    #3. Sort (if sort_by): sort() is stable, even with reverse=True
    #asked to the AI: sort(key=..., reverse=...) -> key chooses the value to sort on
    #(with a lambda, course 9), reverse=True sorts in descending order
    if "sort_by" in query:
        sort_key = query["sort_by"]
        descending = "order" in query and query["order"] == "desc"
        matches.sort(key=lambda flight: flight[sort_key], reverse=descending)

    #4. Limit AFTER the sort (limit 0 -> empty list)
    if "limit" in query:
        matches = matches[:query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    #A single object becomes a list with one element
    if isinstance(queries, dict):
        queries = [queries]

    responses = []
    for query in queries:
        responses.append(run_query(db, query))
    return responses