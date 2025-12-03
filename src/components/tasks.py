from abc import ABC, abstractmethod
import time
from components.sats import Sat
from dataclasses import dataclass
from utils import sample_point_in_spherical_cap



class Task(ABC):
    """任务基类。所有任务需继承并实现 run() 方法。"""

    @abstractmethod
    def run(self):
        """执行任务，返回结果（可选）"""
        pass

@dataclass
class CalDopplerTask(Task):
    sat: Sat
    time: str
    radius: float

    def run(self):
        results = []
        for _ in range(self.n_samples):
            lat, lon = sample_point_in_spherical_cap(self.center_lat, self.center_lon, self.cap_angle_rad)
            doppler, recv = self.sat.doppler_at(self.time_utc, lat, lon, elevation_m=0.0)
            # store tuple (lat, lon, doppler_Hz, recv_Hz)
            results.append((lat, lon, doppler, recv))
        return results