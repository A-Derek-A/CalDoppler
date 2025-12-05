import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))  # my_project/
SRC_PATH = os.path.join(ROOT, "src")
sys.path.insert(0, SRC_PATH)


from skyfield.api import load
from pathlib import Path
from components.sats import Sat
from utils import (
    sample_point_in_spherical_cap,
    footprint_central_angle_rad,
    footprint_surface_radius_km,
)

import math
from vision.viz import viz
import datetime

work_dir = Path(__file__).parent.parent
data_dir = work_dir / "data"


if __name__ == "__main__":
    tles = data_dir / "tle"
    sats = Sat(tles / "57425.tle", 868.1e6)
    t = sats.ts.from_datetime(
        datetime.datetime(2025, 12, 1, 8, 0, 0, tzinfo=datetime.timezone.utc)
    )
    lat, lon, height = sats.pos_at(t)
    print(lat, lon, height)

    sat_altitude_km = 550
    psi = footprint_central_angle_rad(sat_altitude_km)
    radius_km = footprint_surface_radius_km(sat_altitude_km)
    print(f"Altitude: {sat_altitude_km} km")
    print(f"Central angle: {math.degrees(psi):.2f}°")
    print(f"Surface radius: {radius_km:.2f} km")

    points = []
    for _ in range(100):
        la, lo = sample_point_in_spherical_cap(lat, lon, psi)
        points.append((la, lo))

    viz((lat, lon, height), points)
