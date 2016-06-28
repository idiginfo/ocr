#!../idiginfo/bin/python
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
from os import path
import logging, time
logger = logging.getLogger("main")
mainhandler = logging.FileHandler("/data/logs/ocrcronstatus.log", mode="a")
logger.addHandler(mainhandler)
logger.setLevel(logging.DEBUG)
BATCHINPROGRESS = "/data/web/ocr/batchinprogress"
def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]
def get_oldest_file(path):

    try:
        return min(listdir_fullpath(path), key=os.path.getctime)
    except ValueError:
        return None
if len(os.listdir(BATCHINPROGRESS)) == 0:
    os.system('sudo kill -9' + str(os.system('pgrep -f cron_job/batchOCRcontrol.py')))
    print("The process is not running");
    os.system('/data/web/ocr/idiginfo/bin/python3.4 /data/web/ocr/cron_job/batchOCRcontrol.py &> /var/log/ocrcron.log')
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
        os.system('sudo kill -9' + str(os.system('pgrep -f cron_job/batchOCRcontrol.py')))
        logger.info('Process killed')
        os.system('/data/web/ocr/idiginfo/bin/python3.4 /data/web/ocr/cron_job/batchOCRcontrol.py &> /var/log/ocrcron.log')
    else:
        logger.info('Cron is still running!!')

