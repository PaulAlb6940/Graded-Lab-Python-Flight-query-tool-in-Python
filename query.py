"""Running queries against the flight database."""
"""Running queries against the flight database."""


from validator import _is_valid_datetime

RECORD_KEYS = ["flight_id", "origin", "destination",
               "departure_datetime", "arrival_datetime", "price"]
QUERY_KEYS = RECORD_KEYS + ["min_price", "sort_by", "order", "limit"]


def _is_number(value):
    """True si value est un int ou un float, mais PAS un booléen."""
    # À COMPLÉTER : exclure les bool d'abord, puis vérifier int ou float
    if isinstance(value, bool):
        return False
    return isinstance(value, (int, float))



def _is_valid_query(query):
    """True si la requête est valide, False sinon."""
    # 1. Ce n'est pas un dict -> invalide
    if not isinstance(query, dict):
        return False

    # 2. Clé inconnue (ex. "colour") -> invalide
    allowed_keys = ["flight_id", "origin", "destination", "departure_datetime",
                    "arrival_datetime", "price", "min_price", "sort_by", "order", "limit"]
    for key in query:
        if key not in allowed_keys:
            return False

    # 3. flight_id, origin, destination : si présents, ce doivent être des str
    for key in ("flight_id", "origin", "destination"):
        if key in query and not isinstance(query[key], str):
            return False

    # 4. departure_datetime, arrival_datetime : si présents, str ET _is_valid_datetime
    for key in ("departure_datetime", "arrival_datetime"):
        if key in query:
            if not isinstance(query[key], str) or not _is_valid_datetime(query[key]):
                return False

    # 5. price, min_price : si présents, _is_number
    for key in ("price", "min_price"):
        if key in query and not _is_number(query[key]):
            return False

    # 6. limit : si présent, int (pas bool) et >= 0
    if "limit" in query:
        limit = query["limit"]
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
            return False

    # 7. sort_by : si présent, str ET dans RECORD_KEYS
    if "sort_by" in query:
        if not isinstance(query["sort_by"], str) or query["sort_by"] not in RECORD_KEYS:
            return False

    # 8. order : si présent, il faut "sort_by" dans la requête ET la valeur "asc" ou "desc"
    if "order" in query:
        if "sort_by" not in query or query["order"] not in ("asc", "desc"):
            return False

    return True



def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    # 1. Requête invalide -> entrée d'erreur (on n'arrête PAS le programme)
    if not _is_valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    # 2. Filtrer : un vol est gardé seulement s'il remplit TOUTES les conditions (ET)
    matches = []
    for flight in db:
        if "flight_id" in query and flight["flight_id"] != query["flight_id"]:
            continue
        if "origin" in query and flight["origin"] != query["origin"]:
            continue
        if "destination" in query and flight["destination"] != query["destination"]:
            continue
        # les dates au format YYYY-MM-DD HH:MM se comparent correctement comme des textes
        if "departure_datetime" in query and flight["departure_datetime"] < query["departure_datetime"]:
            continue
        if "arrival_datetime" in query and flight["arrival_datetime"] > query["arrival_datetime"]:
            continue
        if "price" in query and flight["price"] > query["price"]:
            continue
        if "min_price" in query and flight["price"] < query["min_price"]:
            continue
        matches.append(flight)

    # 3. Trier (si sort_by) : sorted est stable, même avec reverse=True
    if "sort_by" in query:
        sort_key = query["sort_by"]
        descending = "order" in query and query["order"] == "desc"
        matches = sorted(matches, key=lambda flight: flight[sort_key], reverse=descending)

    # 4. Limiter APRÈS le tri (limit 0 -> liste vide)
    if "limit" in query:
        matches = matches[:query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    # Un objet unique devient une liste d'un seul élément
    if isinstance(queries, dict):
        queries = [queries]

    responses = []
    for query in queries:
        responses.append(run_query(db, query))
    return responses
