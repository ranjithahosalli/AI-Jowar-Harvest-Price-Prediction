from datetime import datetime, timedelta

# Base temperature for Jowar (Sorghum)
TBASE = 10  

# Approximate GDD requirement for maturity
MATURITY_THRESHOLD = 1650  


def compute_gdd(tmin, tmax):
    """Calculate daily Growing Degree Days (GDD)."""
    tmean = (tmin + tmax) / 2
    return max(0, tmean - TBASE)


def predict_harvest_date(sowing_date: datetime, daily_weather: list):
    """
    Predict harvest date using GDD accumulation.
    """
    gdd_sum = 0
    current_date = sowing_date
    i = 0

    while gdd_sum < MATURITY_THRESHOLD:

        if i < len(daily_weather):
            temp_min = daily_weather[i]["temp"]["min"]
            temp_max = daily_weather[i]["temp"]["max"]
        else:
            # Fallback temps when forecast ends
            temp_min = 20
            temp_max = 32

        gdd_sum += compute_gdd(temp_min, temp_max)
        current_date += timedelta(days=1)
        i += 1

    return current_date
