#!venv/bin/python3
"""
this is where we code cron jobs to schedule
"""
import sys
from datetime import datetime
import os
import json
import traceback
import requests
import psutil
from functions import utils
from dotenv import load_dotenv
load_dotenv()

APP_PATH = os.getenv('APP_PATH')
DOMAIN = os.getenv('DOMAIN')
BATCHINPROGRESS = os.path.join(APP_PATH, 'batchinprogress')
BATCHSUBMITTED = os.path.join(APP_PATH, 'batchsubmitted')
BATCHPROCESSED = os.path.join(APP_PATH, 'batchprocessed')
CRON_OUT_LOG = os.path.join(APP_PATH, 'logs', 'ocrcronout.log')
PROCESS_PATH = os.path.join(APP_PATH, 'cron_job.py')

oldest_file_path = ""
inprogress_file_path = ""
import logging, time
logger = logging.getLogger("main")
mainhandler = logging.FileHandler(CRON_OUT_LOG, mode="a")
logger.addHandler(mainhandler)
logger.setLevel(logging.DEBUG)

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

def isBatchInProgress(PROCESS_PATH):
    count = 0
    for proc in psutil.process_iter():
        if PROCESS_PATH in proc.cmdline():
            count=count+1
            if count>1:
                return True
    return False

def get_oldest_file(path):

    try:
        return min(listdir_fullpath(path), key=os.path.getctime)
    except ValueError:
        return None
def process_submitted_files():
    version = utils.get_tesseract_version()
    oldest_file_path = get_oldest_file(BATCHSUBMITTED)
    logger.info(['I am inside processsubmitted files', oldest_file_path])
    starttime = time.strftime("%c")
    modifiedtime = time.strftime("%c")
    filepath = oldest_file_path

    logger.info(os.path.join(BATCHINPROGRESS, os.path.basename(filepath)))

    filealtpath = os.path.join(BATCHINPROGRESS, os.path.basename(filepath))
    filefinalpath = os.path.join(BATCHPROCESSED, os.path.basename(filealtpath))
    logger.info([filepath])
    logger.info([filealtpath])
    jsonobj = json.load(open(filepath, 'r'))
    logger.info([jsonobj])
    logger.info([filepath, 'Constructing Header'])
    jsonobj['header'] = {}
    logger.info([filealtpath, 'adding start and modified time to header'])
    jsonobj['header']['start time'] = starttime
    jsonobj['header']['modified time'] = modifiedtime
    logger.info([filealtpath, 'adding status to in progress'])
    jsonobj['header']['status'] = "in progress"
    logger.info([filealtpath, 'adding total count of subjects'])
    jsonobj['header']['total'] = len(jsonobj['subjects'])
    logger.info([filealtpath, 'adding complete flag and setting it to 0'])
    jsonobj['header']['complete'] = 0
    logger.info([filealtpath, 'adding tesseract version'])
    jsonobj['header']['OCR engine'] = version
    json.dump(jsonobj, open(filealtpath, "w"))
    logger.info([filepath, ' Removing from batchsubmitted folder '])
    os.remove(filepath)
    process_files(filealtpath)
    
def process_files(filealtpath):
    filefinalpath = os.path.join(BATCHPROCESSED, os.path.basename(filealtpath))
    logger.info([filealtpath])
    logger.info([filefinalpath])
    jsonobj = json.load(open(filealtpath, 'r'))
    logger.info([jsonobj, 'The json object is'])
    for elem in jsonobj['subjects']:
        logger.info([filealtpath, ' Working on identifier ', elem])
        logger.info([filealtpath, 'Building URL for ', elem])
        iden = elem
        url = jsonobj['subjects'][elem]['url']
        if (jsonobj['subjects'][elem]['status'] == 'pending'):
            try:
               crop = jsonobj['subjects'][elem]['crop']
            except KeyError as ke:
                logger.info(
                    [filealtpath, elem, ' has no crop value set.'
                        ' Setting to default - no'])
                crop = 'no'
            response = "json"
            jsonobj['subjects'][elem]['messages'] = []
            payload = {'identifier': iden, 'url': url,'crop':crop,'response':response}
            payload = {'identifier': iden, 'url': url,'crop':crop,'response':response}
            buildurl = DOMAIN + "/ocroutput"
            logger.info([filealtpath, ' URL built: ', buildurl])
            resp = requests.get(buildurl,params=payload)
            respjson = resp.json()
            logger.info([respjson, 'the response json is'])
            count = 0
            while respjson['ocr'].isspace():
                logger.info(['trying the URL again'])
                logger.info([count, 'count:'])
                resp = requests.get(buildurl,params=payload)
                respjson = resp.json()
                count = count + 1
                if count>10:
                    os.system('sudo /etc/init.d/apache2 restart')
                    jsonobj['subjects'][elem]['messages'].append(
                      "Output from tesseract is blank")
                    break 
            if resp.status_code == 200:
                respjson = resp.json()
                for message in respjson['messages']:
                    jsonobj['subjects'][elem][
                        'messages'].append(message)
                jsonobj['subjects'][elem]['ocr'] = respjson['ocr']
            else:
                jsonobj['subjects'][elem]['messages'].append(
                    "Response code from " + DOMAIN + " {0}"
                    .format(resp.status_code))
                logger.info(
                    [filealtpath, ' Received status code: ',
                        resp.status_code])
            logger.info(['I am here ocr'])
            if jsonobj['subjects'][elem]['ocr'].isspace():
                jsonobj['subjects'][elem]['status'] = 'error'
            else:
                jsonobj['subjects'][elem]['status'] = 'complete'
            logger.info([filealtpath, ' Incrementing complete count '])
            jsonobj['header']['modified time'] = time.strftime("%c")
            jsonobj['header']["complete"] = int(
                 jsonobj['header']["complete"]) + 1
            with open(filealtpath, "w") as fp:
                json.dump(jsonobj, fp)
            #if jsonobj['header']["complete"] == 200:
                #logger.info('the complete count is 200')
                #os.system('sudo kill -9' + os.system('pgrep -f batch.py'))
    logger.info([filealtpath, ' Modifying status to error or complete '])
    logger.info(['I am done'])
    jsonobj['header']['status'] = 'complete'
    logger.info([filealtpath, ' Dumping json output '])
    with open(filefinalpath, "w") as fp:
        json.dump(jsonobj, fp)
        os.remove(filealtpath)

def cron_jobs():
    """
    logic for doing the cron job of copying over the file
    from batchsubmitted to batchprocessed. Later, building
    url for each identifier in json file and doing a get
    request to single file ocr url, saving the ocr returned
    and dumping back the json file
    """
    version = utils.get_tesseract_version()
    if isBatchInProgress(PROCESS_PATH):
        #logger.info(['Batch in progress'])
        return
    '''inprogress_file_path = get_oldest_file(BATCHINPROGRESS)
    logger.info([inprogress_file_path, 'Inprogress file path'])
    oldest_file_path = get_oldest_file(BATCHSUBMITTED)
    logger.info([oldest_file_path, 'Oldest File Path'])'''
    #if oldest_file_path is None:
        #logger.info(['no files found for batch processing'])            
     #   return    
    try:
       inprogress_file_path = get_oldest_file(BATCHINPROGRESS)
       logger.info([inprogress_file_path, 'Inprogress file path'])
       oldest_file_path = get_oldest_file(BATCHSUBMITTED)
       logger.info([oldest_file_path, 'Oldest File Path'])
       if inprogress_file_path is not None:
            logger.info('calling process_files')
            process_files(inprogress_file_path)
       elif oldest_file_path is not None:
           logger.info('calling process_submitted_files')
           logger.info('about to call process_submitted_files')
           process_submitted_files()
    except Exception as cronexcept:
        logger.info([filealtpath, 'Exception: {0}'.format(cronexcept)])
        logger.info([filealtpath, traceback.format_exc()])

cron_jobs()
