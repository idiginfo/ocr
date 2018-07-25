#!venv/bin/python
"""
this is where we monitor the OCR process
"""
import sys
from datetime import datetime
import os
import json
import traceback
import requests
import psutil
import logging, time
from dotenv import load_dotenv
load_dotenv()

APP_PATH = os.getenv('APP_PATH')
PYTHON_PATH = os.getenv('PYTHON_PATH')
LOG_PATH = os.getenv('LOG_PATH')
BATCHINPROGRESS = os.path.join(APP_PATH, 'batchinprogress')
BATCH_PATH = os.path.join(APP_PATH, 'batch.py')
STATUS_LOG = os.path.join(LOG_PATH, 'ocrcronstatus.log')
CRON_LOG = os.path.join(LOG_PATH, 'ocrcron.log')

logger = logging.getLogger("main")
mainhandler = logging.FileHandler(STATUS_LOG, mode="a")
logger.addHandler(mainhandler)
logger.setLevel(logging.DEBUG)

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

def get_oldest_file(path):

    try:
        print(min(listdir_fullpath(path), key=os.path.getctime))
        return min(listdir_fullpath(path), key=os.path.getctime)
    except ValueError:
        return None
if len(os.listdir(BATCHINPROGRESS)) == 0:
    os.system('sudo kill -9' + str(os.system('pgrep -f cron/batch.py')))
    print("The process is not running");
    os.system(f'{PYTHON_PATH} {BATCH_PATH} &> {CRON_LOG}')
else:
    filepath = get_oldest_file(BATCHINPROGRESS)
    print(filepath);
    jsonobj = json.load(open(filepath, 'r'))
    print("I am inside the status check");
    timestamp2 = jsonobj['header']['modified time'].rstrip()
    timestamp1 = time.strftime("%c").rstrip()
    print(timestamp1);
    print(timestamp2);
    t1 = datetime.strptime(timestamp1, "%a %b %d %H:%M:%S %Y")
    t2 = datetime.strptime(timestamp2, "%a %b %d %H:%M:%S %Y")
    difference = t1 - t2
    logger.info(['The difference between two timestamp are', difference.total_seconds(), difference.days])
    if difference.total_seconds() > 600:
        logger.info('About to restart the cron')
        os.system('sudo kill -9' + str(os.system('pgrep -f cron/batch.py')))
        logger.info('Process killed')
        os.system(f'{PYTHON_PATH} {BATCH_PATH} &> {CRON_LOG}')
    else:
        logger.info('Cron is still running!!')

