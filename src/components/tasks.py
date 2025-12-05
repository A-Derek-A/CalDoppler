from abc import ABC, abstractmethod
import time
from components.sats import Sat
from dataclasses import dataclass
from utils import sample_point_in_spherical_cap, footprint_central_angle_rad
from skyfield.api import Time
from skyfield.toposlib import GeographicPosition, wgs84
from pathlib import Path
from datetime import datetime
from logger import logger
from vision.picture import save_3d_plot_to_file
from vision.viz import viz


@dataclass
class Task(ABC):
    """任务基类。所有任务需继承并实现 run() 方法。"""

    task_id: int

    @abstractmethod
    def run(self):
        """执行任务，返回结果（可选）"""
        pass


@dataclass
class CalDopplerTask(Task):
    """计算多普勒频移任务。"""

    sat: Sat  # 卫星
    time: Time
    n_samples: int  # 子任务点的数量

    def run(self):
        logger.info(
            f"task_id: {self.task_id}, time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        results = []
        lat, lon, height = self.sat.pos_at(self.time)
        # print(f"lat: {lat}, lon: {lon}, height: {height}")
        psi = footprint_central_angle_rad(550, 30)

        logger.info(f"psi: {psi}")
        logger.info(f"n_samples: {self.n_samples}")
        for _ in range(self.n_samples):
            la, lo = sample_point_in_spherical_cap(lat, lon, psi)
            gs = wgs84.latlon(la, lo)
            doppler, received_signal = self.sat.get_doppler(self.time, gs, True)
            results.append((la, lo, doppler, received_signal))

        # 写入文件
        inter_dir = Path(__file__).parent.parent.parent / "data" / "intermediate"
        with open(inter_dir / f"{self.task_id}.txt", "w") as f:
            for la, lo, doppler, received_signal in results:
                f.write(f"{la},{lo},{doppler},{received_signal}\n")
        return results


class MergeTask(Task):
    """合并任务。"""

    def run(self):
        """合并所有子任务的结果。"""
        inter_dir = Path(__file__).parent.parent.parent / "data" / "intermediate"
        final_dir = Path(__file__).parent.parent.parent / "data" / "final"
        final_dir.mkdir(parents=True, exist_ok=True)
        if (final_dir / f"result.txt").exists():
            (final_dir / f"result.txt").unlink()
        with open(final_dir / f"result.txt", "a") as f:
            for file in inter_dir.glob("*.txt"):
                with open(file, "r") as f_in:
                    for line in f_in:
                        f.write(line)
                file.unlink()


class DrawTask(Task):
    """绘制任务。"""

    def run(self):
        """绘制所有子任务的结果。"""
        pic_dir = Path(__file__).parent.parent.parent / "data" / "pics"
        pic_dir.mkdir(parents=True, exist_ok=True)
        data = Path(__file__).parent.parent.parent / "data" / "final"
        res = []
        
        with open(data / f"result.txt", "r") as f:
            for line in f:
                la, lo, doppler, received_signal = line.strip().split(",")
                res.append(
                    (float(la) + 90, float(lo) + 180, float(doppler))
                )
                
        
        save_3d_plot_to_file(res, pic_dir)
        
