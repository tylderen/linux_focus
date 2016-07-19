# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Implements ThreadPoolExecutor."""

__author__ = 'Brian Quinlan (brian@sweetapp.com)'

import atexit
from concurrent.futures import _base
import queue
import threading
import weakref
import os

_threads_queues = weakref.WeakKeyDictionary()
_shutdown = False


def _python_exit():
    global _shutdown
    _shutdown = True
    items = list(_threads_queues.items())
    for t, q in items:
        q.put(None)
    for t, q in items:
        t.join()

atexit.register(_python_exit)

class _WorkItem(object):
    """将 submit 的任务函数进行包装"""
    def __init__(self, future, fn, args, kwargs):
        self.future = future
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        if not self.future.set_running_or_notify_cancel():
            return

        try:
            result = self.fn(*self.args, **self.kwargs)
        except BaseException as e:
            self.future.set_exception(e)
        else:
            self.future.set_result(result)

def _worker(executor_reference, work_queue):
    # 每一个工作线程都会不断的从工作队列里面取任务
    try:
        while True:
            work_item = work_queue.get(block=True)
            if work_item is not None:
                work_item.run()
                # Delete references to object. See issue16284
                del work_item
                continue
            executor = executor_reference()
            # 工作线程退出 可能原因:
            #   - Python 解释器退出
            #   - 线程池被垃圾收集器收集
            #   - 线程池被关闭
            if _shutdown or executor is None or executor._shutdown:
                # Notice other workers
                work_queue.put(None)
                return
            del executor
    except BaseException:
        _base.LOGGER.critical('Exception in worker', exc_info=True)

class ThreadPoolExecutor(_base.Executor):
    def __init__(self, max_workers=None):
        """初始化一个新的线程池对象.

        参数:
            max_workers: 线程池里面最多的工作线程数量.
        """
        if max_workers is None:
            # 如果不显式指定最大工作线程数量, 则默认会指定核数
            # 乘以5的线程数量, 因为线程池执行的任务多是属于I/O
            # 密集型而不是 CPU密集型.
            max_workers = (os.cpu_count() or 1) * 5
        if max_workers <= 0:
            raise ValueError("max_workers must be greater than 0")

        self._max_workers = max_workers
        # 任务队列: 直接使用Python自带的队列
        self._work_queue = queue.Queue()
        self._threads = set()
        self._shutdown = False
        self._shutdown_lock = threading.Lock()

    def submit(self, fn, *args, **kwargs):
        # 使用锁来确保往任务队列里放任务的一系列
        # 行为的正确性.
        with self._shutdown_lock:
            if self._shutdown:
                raise RuntimeError('cannot schedule new futures after shutdown')

            f = _base.Future()
            w = _WorkItem(f, fn, args, kwargs)
            # 将包装好的任务放到任务队列
            self._work_queue.put(w)
            # 增加工作线程的数量,直到达到 max_worker 为止
            self._adjust_thread_count()
            # submit 成功后会返回 future 对象
            return f
    submit.__doc__ = _base.Executor.submit.__doc__

    def _adjust_thread_count(self):
        def weakref_cb(_, q=self._work_queue):
            q.put(None)
        # TODO: 如果已有的工作线程大部分都在空闲的话应避免
        # 再生成新线程.
        if len(self._threads) < self._max_workers:
            t = threading.Thread(target=_worker,
                                 args=(weakref.ref(self, weakref_cb),
                                       self._work_queue))
            t.daemon = True
            # 工作线程启动: 执行 _worker 函数
            t.start()
            self._threads.add(t)
            _threads_queues[t] = self._work_queue

    def shutdown(self, wait=True):
        with self._shutdown_lock:
            self._shutdown = True
            self._work_queue.put(None)
        if wait:
            for t in self._threads:
                t.join()
    shutdown.__doc__ = _base.Executor.shutdown.__doc__