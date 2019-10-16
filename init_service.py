import datetime
import logging
import os
import shutil

EXECUTE_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_D = 'log_kad_arb'
TEMP_D = 'temp_kad_arb'
LOG_DIR = os.path.join(EXECUTE_PATH, LOG_D)
TEMP_DIR = os.path.join(EXECUTE_PATH, TEMP_D)


def create_dirs():
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)
    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)


def init_logger():
    file_log = '{1}/kad_arb_{0}.log'.format(str(datetime.date.today()), LOG_DIR)
    logging.basicConfig(level=logging.DEBUG, filename=file_log,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def initializator():
    create_dirs()
    init_logger()
