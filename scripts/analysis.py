"""Reusable analytical functions. Missing inputs always remain None."""
from math import hypot
from statistics import mean


def normalize_indicator(value, low, high, *, reverse=False):
    if value is None or low is None or high is None or high <= low:
        return None
    score = max(0.0, min(100.0, (value - low) / (high - low) * 100.0))
    return round(100.0 - score if reverse else score, 1)


def calculate_station_distance(x, y, stations):
    distances = [hypot(x - sx, y - sy) for sx, sy in stations]
    return min(distances) if distances else None


def calculate_land_improvement_ratio(land, improvement):
    if land is None or improvement is None or land + improvement <= 0:
        return None
    return round(land / (land + improvement), 4)


def calculate_redevelopment_activity(demolitions=0, new_construction=0, major_alterations=0):
    return float(min(100, demolitions * 40 + new_construction * 25 + major_alterations * 10))


def calculate_redevelopment_pressure(indicators, weights):
    required = [key for key, weight in weights.items() if weight > 0]
    if not required or any(indicators.get(key) is None for key in required):
        return None
    denominator = sum(weights[key] for key in required)
    return round(sum(float(indicators[key]) * weights[key] for key in required) / denominator, 1)


def calculate_renter_exposure(renter_share, renter_households):
    if renter_share is None or renter_households is None:
        return None
    return round(max(0, min(100, renter_share * 100)) * .7 + max(0, min(100, renter_households / 20)) * .3, 1)


def classify_exposure_matrix(pressure, renter_exposure, threshold=50):
    if pressure is None or renter_exposure is None:
        return None
    return f"{'High' if pressure >= threshold else 'Low'} pressure / {'High' if renter_exposure >= threshold else 'Low'} renter exposure"


def summarize_station_area(records):
    rows = list(records)
    scores = [float(row['redevelopment_pressure_score']) for row in rows if row.get('redevelopment_pressure_score') is not None]
    return {'parcel_count': len(rows), 'scored_parcel_count': len(scores), 'mean_pressure': round(mean(scores), 1) if scores else None}


def validate_missing_data(record, required):
    return [field for field in required if record.get(field) is None]
