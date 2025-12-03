import queue
import threading
from concurrent.futures import Future

class TaskExecutor:
    def __init__(self, num_workers=4):
        self.num_workers = num_workers
        self.tasks = queue.Queue()
        self.workers = []
        self.shutdown_flag = threading.Event()

        # 启动 worker 线程
        for _ in range(num_workers):
            t = threading.Thread(target=self._worker_loop)
            t.daemon = True
            t.start()
            self.workers.append(t)

    def submit(self, task):
        """提交任务，返回 future"""
        future = Future()
        self.tasks.put((task, future))
        return future

    def _worker_loop(self):
        while not self.shutdown_flag.is_set():
            try:
                task, future = self.tasks.get(timeout=0.2)
            except queue.Empty:
                continue

            try:
                result = task.run()
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                self.tasks.task_done()

    def shutdown(self, wait=True):
        """停止所有线程"""
        self.shutdown_flag.set()

        if wait:
            for t in self.workers:
                t.join()
    