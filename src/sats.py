from skyfield.api import load
from skyfield.toposlib import GeographicPosition
from pathlib import Path

C = 299792458

class Sat:
    def __init__(self, path: Path, signal_freq: float):
        self.ts = load.timescale()
        self.sat = load.tle_file(str(path))[0]
        self.time_pz = None
        self.signal_freq = signal_freq

    def get_doppler(self, time: str, ground_station: GeographicPosition, debug: bool = False)-> tuple[float, float]:
        t = self.ts.from_utc(time)
        difference = self.sat - ground_station
        topocentric = difference.at(t)
        range_rate_m_s = topocentric.range_rate().m_per_s
        if debug == True:
            print("Range Rate (m/s):", range_rate_m_s)
        doppler_shift = -(range_rate_m_s / C) * self.signal_freq
        if debug == True:
            print("Doppler Shift (Hz):", doppler_shift)
            print("Received Frequency (Hz):", self.signal_freq + doppler_shift)
        return doppler_shift, self.signal_freq + doppler_shift
        

    
        
