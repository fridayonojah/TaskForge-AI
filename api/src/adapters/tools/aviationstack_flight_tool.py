from __future__ import annotations
import re
import requests
import airportsdata
import pycountry
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

from api.src.ports.tools.flight_search_tool import FlightSearchTool

_STOPWORDS = {"flight", "flights", "hotel", "hotels", "trip", "travel", "from", "to", "book", "find", "search"}

_COUNTRY_ALIASES: dict[str, str] = {
    "usa": "united states", "us": "united states", "uk": "united kingdom",
    "uae": "united arab emirates", "emirates": "united arab emirates",
    "south korea": "korea, republic of", "north korea": "korea, democratic people's republic of",
    "russia": "russian federation", "iran": "iran, islamic republic of",
    "syria": "syrian arab republic", "taiwan": "taiwan, province of china",
    "vietnam": "viet nam", "laos": "lao people's democratic republic",
    "tanzania": "tanzania, united republic of", "bolivia": "bolivia, plurinational state of",
    "venezuela": "venezuela, bolivarian republic of", "moldova": "moldova, republic of",
    "congo": "congo, democratic republic of the", "drc": "congo, democratic republic of the",
    "czech republic": "czechia", "türkiye": "turkey", "turkey": "turkey",
    "bangladesh": "bangladesh", "nigeria": "nigeria",
}

_COUNTRY_MAIN_AIRPORT: dict[str, str] = {
    "united states": "JFK", "united kingdom": "LHR", "france": "CDG",
    "germany": "FRA", "japan": "NRT", "china": "PEK", "india": "DEL",
    "australia": "SYD", "canada": "YYZ", "brazil": "GRU",
    "united arab emirates": "DXB", "singapore": "SIN", "thailand": "BKK",
    "malaysia": "KUL", "indonesia": "CGK", "turkey": "IST",
    "saudi arabia": "RUH", "egypt": "CAI", "south africa": "JNB",
    "nigeria": "LOS", "kenya": "NBO", "bangladesh": "DAC",
}

_CITY_MAIN_AIRPORT: dict[str, str] = {
    "new york": "JFK", "london": "LHR", "paris": "CDG", "tokyo": "NRT",
    "dubai": "DXB", "singapore": "SIN", "bangkok": "BKK", "sydney": "SYD",
    "toronto": "YYZ", "frankfurt": "FRA", "amsterdam": "AMS", "hong kong": "HKG",
    "istanbul": "IST", "kuala lumpur": "KUL", "jakarta": "CGK", "beijing": "PEK",
    "shanghai": "PVG", "delhi": "DEL", "mumbai": "BOM", "dhaka": "DAC",
    "los angeles": "LAX", "chicago": "ORD", "miami": "MIA", "cairo": "CAI",
}


class AviationStackFlightTool(FlightSearchTool):
    _BASE_URL = "https://api.aviationstack.com/v1/flights"

    def __init__(self, api_key: str, default_origin: str = "DAC") -> None:
        self._api_key = api_key
        self._default_origin = default_origin
        self._airports = airportsdata.load("IATA")

    def search(self, query: str, limit: int = 10) -> str:
        dep_iata, arr_iata = self._parse_route(query)
        params: dict = {"access_key": self._api_key, "limit": limit, "flight_status": "scheduled"}
        if dep_iata:
            params["dep_iata"] = dep_iata
        if arr_iata:
            params["arr_iata"] = arr_iata
        try:
            data = self._fetch_flights(params)
        except Exception:
            return "Flight data temporarily unavailable. Please try again later."
        flights = data.get("data", [])
        if not flights:
            return "No scheduled flights found for your route."
        return "\n\n".join(self._format_flight(f) for f in flights[:limit])

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=8))
    def _fetch_flights(self, params: dict) -> dict:
        response = requests.get(self._BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def _country_name_to_code(self, text: str) -> str | None:
        normalized = _COUNTRY_ALIASES.get(text.lower(), text.lower())
        try:
            return pycountry.countries.lookup(normalized).alpha_2.lower()
        except LookupError:
            return None

    def _resolve_location_to_iata(self, location: str) -> str | None:
        loc = location.strip().lower()
        if code := _CITY_MAIN_AIRPORT.get(loc):
            return code
        country_name = _COUNTRY_ALIASES.get(loc, loc)
        if code := _COUNTRY_MAIN_AIRPORT.get(country_name):
            return code
        country_code = self._country_name_to_code(loc)
        for iata, info in self._airports.items():
            if (
                (country_code and info.get("country", "").lower() == country_code)
                or info.get("city", "").lower() == loc
                or info.get("name", "").lower().startswith(loc)
            ):
                return iata
        return None

    def _find_location_mentions(self, query: str) -> list[str]:
        known = list(_CITY_MAIN_AIRPORT) + list(_COUNTRY_MAIN_AIRPORT) + list(_COUNTRY_ALIASES)
        return [loc for loc in known if loc in query.lower()]

    def _parse_route(self, query: str) -> tuple[str | None, str | None]:
        q = query.strip().lower()
        if any(kw in q for kw in ("global", "all flights", "international", "worldwide")):
            return None, None
        iata_codes = re.findall(r"\b([A-Z]{3})\b", query.upper())
        if len(iata_codes) >= 2:
            return iata_codes[0], iata_codes[1]
        if len(iata_codes) == 1:
            return self._resolve_location_to_iata(self._default_origin), iata_codes[0]
        m = re.search(r"from\s+(.+?)\s+to\s+(.+?)(?:\s|$)", q)
        if m:
            return self._resolve_location_to_iata(m.group(1)), self._resolve_location_to_iata(m.group(2))
        m = re.search(r"to\s+(.+?)\s+from\s+(.+?)(?:\s|$)", q)
        if m:
            return self._resolve_location_to_iata(m.group(2)), self._resolve_location_to_iata(m.group(1))
        m = re.search(r"to\s+(.+?)(?:\s|$)", q)
        if m:
            return self._resolve_location_to_iata(self._default_origin), self._resolve_location_to_iata(m.group(1))
        locations = self._find_location_mentions(q)
        if len(locations) >= 2:
            return self._resolve_location_to_iata(locations[0]), self._resolve_location_to_iata(locations[1])
        if len(locations) == 1:
            return self._resolve_location_to_iata(self._default_origin), self._resolve_location_to_iata(locations[0])
        return self._resolve_location_to_iata(self._default_origin), None

    def _format_flight(self, flight: dict) -> str:
        dep = flight.get("departure", {})
        arr = flight.get("arrival", {})
        airline = flight.get("airline", {}).get("name", "Unknown Airline")
        fn = flight.get("flight", {}).get("iata", "N/A")
        return (
            f"Flight: {fn} | Airline: {airline}\n"
            f"From: {dep.get('airport', 'N/A')} ({dep.get('iata', 'N/A')}) "
            f"at {dep.get('scheduled', 'N/A')}\n"
            f"To: {arr.get('airport', 'N/A')} ({arr.get('iata', 'N/A')}) "
            f"at {arr.get('scheduled', 'N/A')}\n"
            f"Status: {flight.get('flight_status', 'N/A')}"
        )
