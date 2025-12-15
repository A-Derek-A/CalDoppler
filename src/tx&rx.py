from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from components.simulate import TaskExecutor
from components.tasks import CalDopplerTask, MergeTask, CalReceivedSignalTask, MergeReceivedSignalTask
from components.sats import Sat
from datetime import datetime, timezone
from logger import logger
from vision.picture import save_3d_plot_to_file

work_dir = Path(__file__).parent.parent
data_dir = work_dir / "data"


if __name__ == "__main__":

    

    executor = TaskExecutor()
    future = []
    sat = Sat(data_dir / "tle" / "57425.tle", 868.1e6)
    
    all_nums = 10000
    sub_nums = 100
    task_num = all_nums // sub_nums

    # 记录 futures
    futures = []
    for i in range(task_num):
        task = CalDopplerTask(
            task_id=i,
            sat=sat,
            time=sat.ts.from_datetime(
                datetime(2025, 12, 1, 8, 0, 0, tzinfo=timezone.utc)
            ),
            n_samples=sub_nums,
        )
        futures.append(executor.submit(task))
    

    # 等待所有前置任务完成
    for f in futures:
        f.result()
        logger.info(f"{f}")
        

    # 再提交 merge 任务
    merge_task = MergeTask(task_id=task_num)
    executor.submit(merge_task).result()

    res = []

    with open(data_dir / f"final" / "result.txt", "r") as f:
        for line in f:
            la, lo, doppler, signal = line.strip().split(",")
            logger.info(f"{la}, {lo}, {doppler}, {signal}")
            res.append((float(la), float(lo), float(doppler), float(signal)))

    logger.info(f"{len(res)=}")

    futures = []
    for i in range(task_num):
        task = CalReceivedSignalTask(
            task_id=i,
            sat=sat,
            time=sat.ts.from_datetime(
                datetime(2025, 12, 1, 8, 0, 0, tzinfo=timezone.utc)
            ),
            n_samples=sub_nums,
            offset = res[0][2]
        )
        futures.append(executor.submit(task))
        logger.info(f"submit task done")
    ref_x = res[0][0]
    ref_y = res[0][1]
    offset = res[0][2]

    logger.info(f"here")
    for f in futures:
        f.result()
        logger.info(f"{f}")
    merge_task = MergeReceivedSignalTask(task_id=task_num)
    executor.submit(merge_task).result()
    logger.info(f"merge task done")

    executor.shutdown()
    
    pic_dir = Path(__file__).parent.parent / "data" / "pics"
    pic_dir.mkdir(parents=True, exist_ok=True)
    data = Path(__file__).parent.parent / "data" / "final"
    res = []
    vis_point = []
    logger.info(task_num)
    with open(data / f"result-received-signal.txt", "r") as f:
        for line in f:
            la, lo, doppler, received_signal = line.strip().split(",")
            res.append(
                (float(la) + 180, float(lo) + 180, float(doppler))
            )
            vis_point.append((float(la), float(lo), 0))
    logger.info(f"{len(res)=}")
    res.append((ref_x + 180, ref_y + 180, offset))
    save_3d_plot_to_file(res, pic_dir)
    
    