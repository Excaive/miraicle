import threading
import queue
import contextlib
from typing import List, Tuple, Callable


class ThreadPool:
    def __init__(self, core_pool_size: int = 0, max_pool_size: int = 16, timeout: float = 60.):
        self.core_pool_size: int = core_pool_size
        self.max_pool_size: int = max_pool_size
        self.timeout: float = timeout

        self.__queue: queue.Queue = queue.Queue()
        self.__threads: List[str] = []
        self.__free_threads: List[str] = []

    def add_task(self, target: Callable, args: Tuple = ()):
        self.__queue.put((target, args))
        if not self.__free_threads and len(self.__threads) < self.max_pool_size:
            new_thread = threading.Thread(target=self.__call)
            new_thread.start()

    def __call(self):
        current_thread = threading.currentThread().getName()
        with self.__worker_state(self.__threads, current_thread):
            while True:
                try:
                    with self.__worker_state(self.__free_threads, current_thread):
                        func, args = self.__queue.get(timeout=self.timeout)
                    func(*args)
                except queue.Empty:
                    if len(self.__threads) > self.core_pool_size:
                        break

    @staticmethod
    @contextlib.contextmanager
    def __worker_state(thread_list: List[str], thread_name: str):
        thread_list.append(thread_name)
        try:
            yield
        finally:
            thread_list.remove(thread_name)
