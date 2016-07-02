# -*- coding: utf-8 -*-
from __future__ import absolute_import

import time
import signal
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


def sig_alarm():
    ret1 = signal.alarm(0)
    ret2 = signal.alarm(5)
    time.sleep(1)
    ret3 = signal.alarm(2)
    logging.info(ret1)
    logging.info(ret2)
    logging.info(ret3)


def get_signal(signal_num):
    # get SIG_'s handler
    ret = signal.getsignal(signal_num)
    logging.info(ret)


if __name__ == '__main__':
    sig_alarm()

    logging.info(get_signal(signal.SIGALRM))

    signal.pause()