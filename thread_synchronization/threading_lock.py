# -*- coding: utf-8 -*-
import threading
import time
from concurrent.futures import ThreadPoolExecutor

lock = threading.Lock()
count = 0


def plus_without_lock():
    global count
    count += 1


def plus_with_lock():
    global count
    with lock:
        count += 1


if __name__ == '__main__':
    print('Without lock:')
    with ThreadPoolExecutor(max_workers=100) as executor:
        for _ in xrange(3):
            for _ in xrange(10000):
                executor.submit(plus_without_lock)
            time.sleep(2)
            print(count)
            count = 0

    print('With lock:')
    with ThreadPoolExecutor(max_workers=100) as executor:
        for _ in xrange(3):
            for _ in xrange(10000):
                executor.submit(plus_with_lock)
            time.sleep(2)
            print(count)
            count = 0
