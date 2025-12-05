from components.sats import Sat
from pathlib import Path
from datetime import datetime, timezone
from skyfield.api import wgs84

def sat_test():
    tle_path = Path(__file__).parent.parent / "data" / "tle"
    sat = Sat(tle_path / "57425.tle", 868.1e6)
    time = sat.ts.from_datetime(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
    lat, lon, height = sat.pos_at(time)
    doppler_shift, received_freq = sat.get_doppler(
        time=time,
        ground_station= wgs84.latlon(lat, lon),
        debug=True
    )
    assert(doppler_shift != 0)

