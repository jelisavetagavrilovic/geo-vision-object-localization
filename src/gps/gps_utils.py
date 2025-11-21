import math

def dms_to_decimal(dms_str: str) -> float:
    parts = dms_str.replace(" deg", "").replace("'", "").replace('"', "").split()
    degrees, minutes, seconds, direction = float(parts[0]), float(parts[1]), float(parts[2]), parts[3]

    decimal = degrees + minutes / 60 + seconds / 3600

    if direction in ["S", "W"]:
        decimal = -decimal

    return decimal


def calculate_bearing(lat1, lon1, lat2, lon2):
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δλ = math.radians(lon2 - lon1)

    x = math.sin(Δλ) * math.cos(φ2)
    y = math.cos(φ1) * math.sin(φ2) - math.sin(φ1) * math.cos(φ2) * math.cos(Δλ)

    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360
