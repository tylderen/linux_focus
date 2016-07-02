import time
import signal
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


def sigalarm_handler(signum, frame):
    # signal handler function
    logging.info('In SIGALARM\'s handler')
    exit()


def sigint_handler(signum, frame):
    logging.info('In SIGINT\'s handler')
    exit()


def main():

    # register signal.SIGALRM's handler
    signal.signal(signal.SIGALRM, sigalarm_handler)

    # register signal.SIGINT's handler.
    # if uncomment next line, it will Override the KeyboardInterrupt.
    # signal.signal(signal.SIGINT, int_handler)

    # get SIGINT's handler
    logging.info(signal.getsignal(signal.SIGINT))
    # get SIGALARM's handler
    logging.info(signal.getsignal(signal.SIGALRM))

    try:
        while True:
            time.sleep(0.2)
            logging.info('No signal arrive.')
    except KeyboardInterrupt: # Default: SIGINT is translated into a KeyboardInterrupt exception.
        logging.info('KeyboardInterrupt')



if __name__ == '__main__':
    main()
