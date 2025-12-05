import queue
import threading
from concurrent.futures import Future

_SENTINEL = object()


class TaskExecutor:
    def __init__(self, num_workers=4):
        self.num_workers = num_workers
        self.tasks = queue.Queue()
        self.shutdown_flag = False
        self.workers = []

        for _ in range(num_workers):
            t = threading.Thread(target=self._worker_loop)
            t.start()
            self.workers.append(t)

    def submit(self, task):
        if self.shutdown_flag:
            raise RuntimeError("Cannot submit task after shutdown()")

        future = Future()
        self.tasks.put((task, future))
        return future

    def _worker_loop(self):
        while True:
            item = self.tasks.get()
            if item is _SENTINEL:
                self.tasks.task_done()
                break

            task, future = item
            try:
                result = task.run()
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                self.tasks.task_done()

    def shutdown(self, wait=True):
        """等待所有任务执行完并安全关闭线程。"""

        self.shutdown_flag = True

        # 插入 num_workers 个哨兵，保证每个线程都能退出
        for _ in range(self.num_workers):
            self.tasks.put(_SENTINEL)

        if wait:
            # 等待任务队列被标记完成
            self.tasks.join()

            # 等待所有线程退出
            for t in self.workers:
                t.join()
