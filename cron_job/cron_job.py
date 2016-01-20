#!../idiginfo/bin/python
"""
this is where we code cron jobs to schedule
"""
import sys
import os
sys.path.insert(1, '/home/shiva/Desktop/ocr/idiginfo-ocr')
import json
import traceback
import requests
import psutil
from os import path
from businesslogic import utils
BATCHSUBMITED = utils.get_property('BATCHSUBMITED')
BATCHPROCESSED = utils.get_property('BATCHPROCESSED')
process_path = "/data/web/ocr/cron_job/cron_job.py"

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

def isBatchInProgress(process_path):
    count = 0
    for proc in psutil.process_iter():
        if process_path in proc.cmdline():
            count=count+1
            if count>1:
                return True
    return False

def get_oldest_file(path):
    try:
        return min(listdir_fullpath(path), key=os.path.getctime)
    except ValueError:
        return None

def cron_jobs():
    """
    logic for doing the cron job of copying over the file
    from batchsubmited to batchprocessed. Later, building
    url for each identifier in json file and doing a get
    request to single file ocr url, saving the ocr returned
    and dumping back the json file
    """
    import logging, time
    logger = logging.getLogger("main")
    mainhandler = logging.FileHandler("/data/logs/cron.out", mode="a")
    logger.addHandler(mainhandler)
    logger.setLevel(logging.DEBUG)
    version = utils.get_tesseract_version()
    #logger.info(["tesseract version:",version])
    #for root, dirnames, files in os.walk(BATCHSUBMITED):
    #    for file in files:
    #        try:
    if isBatchInProgress(process_path):
        #logger.info(['Batch in progress'])
        return
    oldest_file_path = get_oldest_file(BATCHSUBMITED)
    if oldest_file_path is None:
        #logger.info(['no files found for batch processing'])            
        return    
    try:    
        starttime = time.strftime("%c")
        modifiedtime = time.strftime("%c") 
        filepath = oldest_file_path
        filealtpath = os.path.join(BATCHPROCESSED, os.path.basename(filepath))
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
        #jsonobj['header']['OCR engine version'] = version
        json.dump(jsonobj, open(filealtpath, "w"))
        logger.info([filepath, ' Removing from batchsubmited folder '])
        os.remove(filepath)
        for elem in jsonobj['subjects']:
            logger.info([filealtpath, ' Working on identifier ', elem])
            logger.info([filealtpath, 'Building URL for ', elem])
            iden = elem
            url = jsonobj['subjects'][elem]['url']
            try:
                crop = jsonobj['subjects'][elem]['crop']
            except KeyError as ke:
                logger.info(
                    [filealtpath, elem, ' has no crop value set.'
                        ' Setting to default - no'])
                crop = 'no'
            response = "json"
            jsonobj['subjects'][elem]['messages'] = []
            jsonobj['subjects'][elem]['ocr'] = ''
            payload = {'identifier': iden, 'url': url,'crop':crop,'response':response}
            buildurl = "http://ocr.idiginfo.org/ocroutput"
            logger.info([filealtpath, ' URL built: ', buildurl])
            resp = requests.get(buildurl,params=payload)
            if resp.status_code == 200:
                respjson = resp.json()
                for message in respjson['messages']:
                    jsonobj['subjects'][elem][
                        'messages'].append(message)
                jsonobj['subjects'][elem]['ocr'] = respjson['ocr']
            else:
                jsonobj['subjects'][elem]['messages'].append(
                    "Response code from ocr.idiginfo.org {0}"
                    .format(resp.status_code))
                logger.info(
                    [filealtpath, ' Received status code: ',
                        resp.status_code])
            jsonobj['subjects'][elem]['status'] = 'complete'
            logger.info([filealtpath, ' Incrementing complete count '])
            jsonobj['header']['modified time'] = time.strftime("%c")
            jsonobj['header']["complete"] = int(
                jsonobj['header']["complete"]) + 1
            with open(filealtpath, "w") as fp:
                json.dump(jsonobj, fp)
        logger.info([filealtpath, ' Modifying status to error or complete '])
        # if respjson['messages']:
        #    jsonobj['header']['status'] = 'error'
        # else:
        jsonobj['header']['status'] = 'complete'
        logger.info([filealtpath, ' Dumping json output '])
        with open(filealtpath, "w") as fp:
            json.dump(jsonobj, fp)
    except Exception as cronexcept:
        logger.info([filealtpath, 'Exception: {0}'.format(cronexcept)])
        logger.info([filealtpath, traceback.format_exc()])

cron_jobs()

