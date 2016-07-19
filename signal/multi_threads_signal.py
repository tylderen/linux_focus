# -*- coding: utf-8 -*-
import time
import signal
import logging
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

is_exit = False


def work():
    global is_exit
    current_thread = threading.current_thread()
    index = 0
    while not is_exit:
        if (index < 4):
            logging.info('%s:  %d', current_thread, index)
            index += 1
        else:
            break
        time.sleep(1)

    logging.info('%s complete.' , str(current_thread))


def handler(signum, frame):
    global is_exit
    is_exit = True
    current_thread = threading.current_thread()
    logging.info('%s receive a signal %d, is_exit = %d', current_thread, signum, is_exit)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    threads = []
    threads_num = 2
    for i in range(threads_num):
        t = threading.Thread(target=work)
        t.setDaemon(True)
        t.start()
        threads.append(t)

    try:
        while threads:
            for t in threads:
                if not t.isAlive():
                  threads.remove(t)
            time.sleep(0.1)
    except:
        pass