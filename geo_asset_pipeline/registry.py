# Geo Registry for Greater Sacramento & Gold Standard Local SEO
import math

DEFAULT_BUSINESS = {
    "name": "Gold Standard Local SEO",
    "legal_name": "Gold Standard Assets LLC",
    "street_address": "705 Gold Lake Dr Ste 250",
    "city": "Folsom",
    "state": "CA",
    "postal_code": "95630",
    "country": "US",
    "phone": "+1-916-234-3457",
    "display_phone": "(916) 234-3457",
    "email": "inquiry@gslocalseo.com",
    "website": "https://www.gslocalseo.com",
    "cid": "7895656689241912038",
    "cid_url": "https://maps.google.com/?cid=7895656689241912038",
    "gmaps_url": "https://maps.app.goo.gl/CNYhmjUuTFXRdGHj7",
    "regional_hub": "https://www.google.com/maps/d/viewer?mid=1LzWpHQrr6pl_KZQ-MyVaRnHs8bEHezc",
}

CITIES = {
    "folsom": {
        "name": "Folsom",
        "state": "CA",
        "county": "Sacramento County",
        "lat": 38.605544,
        "lon": -121.183846,
        "altitude_m": 67,
        "zip_codes": ["95630", "95671"],
        "landmarks": ["705 Gold Lake Dr", "Sutter Street Historic District", "Folsom Lake State Recreation Area", "Lake Natoma", "American River Bike Trail"],
        "neighborhoods": ["Historic Folsom", "Broadstone", "Empire Ranch", "Prairie Oaks", "Willow Creek"]
    },
    "roseville": {
        "name": "Roseville",
        "state": "CA",
        "county": "Placer County",
        "lat": 38.752124,
        "lon": -121.288006,
        "altitude_m": 50,
        "zip_codes": ["95661", "95678", "95747"],
        "landmarks": ["Westfield Galleria at Roseville", "Fountains at Roseville", "Vernon Street Town Square", "Mahany Park"],
        "neighborhoods": ["Highland Reserve", "Woodcreek", "Blue Oaks", "Sun City Roseville", "Diamond Creek"]
    },
    "rocklin": {
        "name": "Rocklin",
        "state": "CA",
        "county": "Placer County",
        "lat": 38.790734,
        "lon": -121.235788,
        "altitude_m": 79,
        "zip_codes": ["95677", "95765"],
        "landmarks": ["Quarry Park Adventures", "Sierra College", "Whitney Oaks Golf Club"],
        "neighborhoods": ["Whitney Ranch", "Stanford Ranch", "Sunset Whitney", "Clover Valley"]
    },
    "granite_bay": {
        "name": "Granite Bay",
        "state": "CA",
        "county": "Placer County",
        "lat": 38.742401,
        "lon": -121.179948,
        "altitude_m": 85,
        "zip_codes": ["95746"],
        "landmarks": ["Granite Bay Golf Club", "Folsom Lake State Recreation Area Beach", "Douglas Blvd Corridor"],
        "neighborhoods": ["Los Lagos", "Treelake Village", "Shelborne", "Wexford"]
    },
    "el_dorado_hills": {
        "name": "El Dorado Hills",
        "state": "CA",
        "county": "El Dorado County",
        "lat": 38.685736,
        "lon": -121.082174,
        "altitude_m": 234,
        "zip_codes": ["95762"],
        "landmarks": ["El Dorado Hills Town Center", "Serrano Country Club", "Folsom Lake South Shore"],
        "neighborhoods": ["Serrano", "The Promontory", "Blackstone", "Governor\'s Park", "Watermark"]
    },
    "citrus_heights": {
        "name": "Citrus Heights",
        "state": "CA",
        "county": "Sacramento County",
        "lat": 38.707125,
        "lon": -121.291341,
        "altitude_m": 51,
        "zip_codes": ["95610", "95621"],
        "landmarks": ["Sunrise Mall", "Sunrise Marketplace", "Rusch Community Park"],
        "neighborhoods": ["Arcade Creek", "Birdcage Heights", "Greenback Wood"]
    },
    "fair_oaks": {
        "name": "Fair Oaks",
        "state": "CA",
        "county": "Sacramento County",
        "lat": 38.644625,
        "lon": -121.272173,
        "altitude_m": 53,
        "zip_codes": ["95628"],
        "landmarks": ["Fair Oaks Village", "Plaza Park Chickens", "Sailor Bar American River"],
        "neighborhoods": ["Fair Oaks Bluffs", "Rollingwood", "Phoenix Field"]
    },
    "rancho_cordova": {
        "name": "Rancho Cordova",
        "state": "CA",
        "county": "Sacramento County",
        "lat": 38.589073,
        "lon": -121.302728,
        "altitude_m": 27,
        "zip_codes": ["95670", "95742"],
        "landmarks": ["Mather Airport", "Sacramento State Aquatic Center", "Sunrise Blvd Commercial Hub"],
        "neighborhoods": ["Anatolia", "Sunridge Park", "Villages of Zinfandel"]
    },
    "sacramento": {
        "name": "Sacramento",
        "state": "CA",
        "county": "Sacramento County",
        "lat": 38.581572,
        "lon": -121.494400,
        "altitude_m": 9,
        "zip_codes": ["95814", "95816", "95819", "95825", "95833"],
        "landmarks": ["California State Capitol", "Golden 1 Center", "DOCO Downtown Commons", "Old Sacramento Waterfront", "Midtown Sacramento"],
        "neighborhoods": ["Downtown", "Midtown", "East Sacramento", "Land Park", "Natomas", "Pocket"]
    },
    "elk_grove": {
        "name": "Elk Grove",
        "state": "CA",
        "county": "Sacramento County",
        "lat": 38.408799,
        "lon": -121.371618,
        "altitude_m": 14,
        "zip_codes": ["95624", "95757", "95758"],
        "landmarks": ["Old Town Elk Grove", "Elk Grove Regional Park", "District56"],
        "neighborhoods": ["Laguna West", "East Elk Grove", "Madeira", "Sheldon"]
    }
}

def get_city_geo(city_input):
    if not city_input:
        return CITIES["folsom"]
    key = city_input.strip().lower().replace(" ", "_").replace("-", "_")
    if key in CITIES:
        return CITIES[key]
    for k, v in CITIES.items():
        if k in key or key in k:
            return v
    # Fallback to Folsom HQ
    return CITIES["folsom"]

def decimal_to_dms_rational(deg_float):
    deg = int(abs(deg_float))
    min_float = (abs(deg_float) - deg) * 60.0
    minute = int(min_float)
    sec_float = (min_float - minute) * 60.0
    sec_int = int(round(sec_float * 100))
    return ((deg, 1), (minute, 1), (sec_int, 100))

def format_iso6709(lat, lon, alt=0):
    lat_sign = "+" if lat >= 0 else "-"
    lon_sign = "+" if lon >= 0 else "-"
    return f"{lat_sign}{abs(lat):.4f}{lon_sign}{abs(lon):.4f}/"
