from components.simulate import TaskExecutor
from components.sats import Sat
from pathlib import Path
from components.tasks import TempCalFootprintTask, MergeTask, MergeFootprintTask, CalDopplerTask
from logger import logger
from datetime import datetime, timezone
from vision.picture import plot_footprint

work_dir = Path(__file__).parent.parent
data_dir = work_dir / "data"


if __name__ == "__main__":
    executor = TaskExecutor()

    all_nums = 10000
    sub_nums = 1000
    task_num = all_nums // sub_nums

    sat1 = Sat(data_dir / "tle" / "66206.tle", 868.1e6)
    sat2 = Sat(data_dir / "tle" / "66208.tle", 868.1e6)

    # 记录 futures
    futures = []
    for id in range(2):
        for i in range(task_num):
            task = TempCalFootprintTask(
                task_id=i + id * task_num,
                sat=sat1 if id == 0 else sat2,
                time=sat1.ts.from_datetime(
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
    merge_task = MergeFootprintTask(task_id=task_num * 2)
    executor.submit(merge_task).result()

    executor.shutdown()

    pic_dir = Path(__file__).parent.parent / "data" / "pics"
    pic_dir.mkdir(parents=True, exist_ok=True)
    data = Path(__file__).parent.parent / "data" / "final"
    res = []
    vis_point = []
    logger.info(task_num)
    with open(data / f"result-footprint.txt", "r") as f:
        for line in f:
            la, lo, doppler, received_signal = line.strip().split(",")
            res.append(
                (float(la) + 180, float(lo) + 180, float(doppler))
            )
            vis_point.append((float(la), float(lo), float(doppler)))
    logger.info(f"{len(res)=}")
    # save_3d_plot_to_file(res, pic_dir)
    # print(res)
    plot_footprint(res, pic_dir)
