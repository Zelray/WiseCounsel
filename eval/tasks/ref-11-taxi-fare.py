"""Reference solution for task 11 - T1-taxi-fare."""
import math

FLAG_DROP_CENTS = 300
DAY_RATE_CENTS_PER_TENTH = 25
NIGHT_RATE_CENTS_PER_TENTH = 31
DAY_START_HOUR = 5
DAY_END_HOUR = 21
AIRPORT_FLAT_CENTS = 4200
MINIMUM_FARE_CENTS = 800
ROUND_TO_CENTS = 50


def taxi_fare(distance_miles, start_hour, airport):
    """Return the fare in dollars for one ride, or -1.0 for an unusable request."""
    if isinstance(distance_miles, bool) or not isinstance(distance_miles, (int, float)):
        return -1.0
    if distance_miles < 0:
        return -1.0
    if isinstance(start_hour, bool) or not isinstance(start_hour, int):
        return -1.0
    if not 0 <= start_hour <= 23:
        return -1.0
    if not isinstance(airport, bool):
        return -1.0

    if airport:
        return AIRPORT_FLAT_CENTS / 100

    tenths = math.ceil(round(distance_miles * 10, 6))
    rate = (DAY_RATE_CENTS_PER_TENTH
            if DAY_START_HOUR <= start_hour <= DAY_END_HOUR
            else NIGHT_RATE_CENTS_PER_TENTH)
    metered = FLAG_DROP_CENTS + rate * tenths
    if metered < MINIMUM_FARE_CENTS:
        metered = MINIMUM_FARE_CENTS

    rounded = math.floor(metered / ROUND_TO_CENTS + 0.5) * ROUND_TO_CENTS
    return rounded / 100
