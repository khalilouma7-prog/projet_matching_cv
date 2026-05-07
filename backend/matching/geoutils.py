from typing import Optional, Tuple

# Basic city geocoding for project demo scope (Morocco-focused).
CITY_COORDS = {
    "casablanca": (33.5731, -7.5898),
    "rabat": (34.0209, -6.8416),
    "marrakech": (31.6295, -7.9811),
    "fes": (34.0331, -5.0003),
    "fes meknes": (34.0331, -5.0003),
    "meknes": (33.8935, -5.5473),
    "tanger": (35.7595, -5.8340),
    "agadir": (30.4278, -9.5981),
    "kenitra": (34.2610, -6.5802),
    "oujda": (34.6814, -1.9086),
    "tetouan": (35.5889, -5.3626),
    "el jadida": (33.2316, -8.5007),
    "safi": (32.2994, -9.2372),
    "nador": (35.1681, -2.9287),
    "beni mellal": (32.3373, -6.3498),
    "ben guerir": (32.2359, -7.9545),
}


def geocode_city(location_text: str) -> Tuple[Optional[float], Optional[float]]:
    """Resolve a location text to (lat, lng) using known city dictionary."""
    if not location_text:
        return None, None

    normalized = location_text.strip().lower()
    if normalized in CITY_COORDS:
        return CITY_COORDS[normalized]

    for city, coords in CITY_COORDS.items():
        if city in normalized:
            return coords

    return None, None