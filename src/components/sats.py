from skyfield.api import load
from skyfield.toposlib import GeographicPosition
from skyfield.api import Time, wgs84
from pathlib import Path
import math
import numpy as np

C = 299792458


class Sat:
    def __init__(self, path: Path, signal_freq: float):
        self.ts = load.timescale()
        self.sat = load.tle_file(str(path))[0]
        self.time_pz = None
        self.signal_freq = signal_freq

    def pos_at(self, time: Time) -> tuple[float, float, np.float64]:
        """calculate (lat, lon, height) of the satellite at a given time (utc)

        Args:
            time (Time): skfield.timelib.Time

        Returns:
            lat (°), lon (°), height (km)
        """
        geocentric = self.sat.at(time)
        subpoint = wgs84.subpoint(geocentric)
        lat = math.degrees(subpoint.latitude.radians)
        lon = math.degrees(subpoint.longitude.radians)
        height = subpoint.elevation.km

        return lat, lon, height

    def get_doppler(
        self, time: Time, ground_station: GeographicPosition, debug: bool = False
    ) -> tuple[float, float]:

        # 方法1：最推荐（最简洁、最不容易出错）
        gs = wgs84.latlon(
            ground_station.latitude.degrees,
            ground_station.longitude.degrees,
            elevation_m=0,
        )

        topocentric = (self.sat - gs).at(time)  # 关键！卫星 - 地面站

        _, _, topo_range, _, _, topo_range_rate = topocentric.frame_latlon_and_rates(
            ground_station
        )
        doppler_shift = -1 * self.signal_freq * topo_range_rate.m_per_s / C

        if debug:
            print("Range Rate (m/s):", topo_range_rate.m_per_s)

        if debug:
            print("Doppler Shift (Hz):", doppler_shift)
            print("Received Frequency (Hz):", self.signal_freq + doppler_shift)

        return doppler_shift, self.signal_freq + doppler_shift
