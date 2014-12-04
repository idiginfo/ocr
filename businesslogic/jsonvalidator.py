#!../idiginfo/bin/python
"""
this is business logic for validating json file
"""
import json
from flask import flash
from businesslogic import utils
import os
from app import app
def validate_json(fileupload):
    if fileupload and utils.allowed_file(fileupload.filename):
        fileloc = os.path.join(app.config['BATCHSUBMITED'], fileupload.filename)
        fileupload.save(fileloc)
        feedback = validate_json_format(fileloc)
        if not feedback:
            return fileupload.filename
        else:
            for each in feedback:
                flash(each)
            return False 
    else:
        flash("Submit a json file") 
        return False

def validate_json_format(fileloc):
    try:
        errorlist = []
        jsonobj = json.load(open(fileloc,'r'))
        if jsonobj.get('list',False):
            for obj in jsonobj['list']:
                url = jsonobj['list'][obj].get("url",None)
                if url is None or url == '':
                    errorlist.append(str(obj)+" has no url field")
        return errorlist
            
    except Exception as loadexcept:
        errorlist.append("Problem opening json file.")
        errorlist.append(loadexcept)
        return errorlist
