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
from businesslogic import utils
BATCHSUBMITED = utils.get_property('BATCHSUBMITED')
BATCHPROCESSED = utils.get_property('BATCHPROCESSED')


def cron_jobs():
    """
    logic for doing the cron job of copying over the file
    from batchsubmited to batchprocessed. Later, building
    url for each identifier in json file and doing a get
    request to single file ocr url, saving the ocr returned
    and dumping back the json file
    """
    import logging
    logger = logging.getLogger("main")
    mainhandler = logging.FileHandler("/home/shiva/logs/cron.out", mode="a")
    logger.addHandler(mainhandler)
    logger.setLevel(logging.DEBUG)
    for root, dirnames, files in os.walk(BATCHSUBMITED):
        for file in files:
            try:
                filepath = os.path.join(BATCHSUBMITED, file)
                filealtpath = os.path.join(BATCHPROCESSED, file)
                if file == 'sampleformat.json':
                    continue
                logger.info([file])
                jsonobj = json.load(open(filepath, 'r'))
                logger.info([file, 'Modifying status to In progress'])
                jsonobj['header']['status'] = "In progress"
                json.dump(jsonobj, open(filealtpath, "w"))
                logger.info([file, ' Removing from batchsubmited folder '])
                os.remove(filepath)
                for elem in jsonobj['subjects']:
                    logger.info([file, ' Working on identifier ', elem])
                    logger.info([file, 'Building URL for ', elem])
                    iden = elem
                    url = jsonobj['subjects'][elem]['url']
                    try:
                        crop = jsonobj['subjects'][elem]['crop']
                    except KeyError as ke:
                        logger.info(
                            [file, elem, ' has no crop value set.'
                             ' Setting to default - no'])
                        crop = 'no'
                    response = "json"
                    jsonobj['subjects'][elem]['messages'] = []
                    jsonobj['subjects'][elem]['ocr'] = ''
                    buildurl = "http://localhost:5000/ocroutput?identifier="\
                        "{0}&url={1}&crop={2}&response={3}".format(
                            iden, url, crop, response)
                    logger.info([file, ' URL built: ', buildurl])
                    resp = requests.get(buildurl)
                    if resp.status_code == 200:
                        respjson = resp.json()
                        for message in respjson['messages']:
                            jsonobj['subjects'][elem][
                                'messages'].append(message)
                        jsonobj['subjects'][elem]['ocr'] = respjson['ocr']
                    else:
                        jsonobj['subjects'][elem]['messages'].append(
                            "Response code from ocr.dev.morphbank.net {0}"
                            .format(resp.status_code))
                        logger.info(
                            [file, ' Received status code: ',
                                   resp.status_codes])
                    jsonobj['subjects'][elem]['complete'] = 'yes'
                    logger.info([file, ' Incrementing complete count '])
                    jsonobj['header']["Complete"] = int(
                        jsonobj['header']["Complete"]) + 1
                    json.dump(jsonobj, open(filealtpath, "w"))
                logger.info([file, ' Modifying status to Complete '])
                jsonobj['header']['status'] = 'Complete'
                logger.info([file, ' Dumping json output '])
                json.dump(jsonobj, open(filealtpath, "w"))
            except Exception as cronexcept:
                logger.info([file, 'Exception: {0}'.format(cronexcept)])
                logger.info([file, traceback.format_exc()])

cron_jobs()
