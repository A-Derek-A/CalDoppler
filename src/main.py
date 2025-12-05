from components.tasks import CalDopplerTask, MergeTask, DrawTask
from components.simulate import TaskExecutor
from components.sats import Sat
from pathlib import Path
from datetime import datetime, timezone
from vision.picture import save_3d_plot_to_file
from vision.viz import viz
from logger import logger

work_dir = Path(__file__).parent.parent
data_dir = work_dir / "data"

if __name__ == "__main__":
    executor = TaskExecutor()

    all_nums = 10000
    sub_nums = 100
    task_num = all_nums // sub_nums

    sat = Sat(data_dir / "tle" / "57425.tle", 868.1e6)

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

    # 再提交 draw 任务
    # draw_task = DrawTask(task_id=task_num + 1)
    # executor.submit(draw_task).result()

    executor.shutdown()
    pic_dir = Path(__file__).parent.parent / "data" / "pics"
    pic_dir.mkdir(parents=True, exist_ok=True)
    data = Path(__file__).parent.parent / "data" / "final"
    res = []
    vis_point = []
    logger.info(task_num)
    with open(data / f"result.txt", "r") as f:
        for line in f:
            la, lo, doppler, received_signal = line.strip().split(",")
            res.append(
                (float(la) + 180, float(lo), float(doppler))
            )
            vis_point.append((float(la), float(lo), 0))
    logger.info(f"{len(res)=}")
    save_3d_plot_to_file(res, pic_dir)
