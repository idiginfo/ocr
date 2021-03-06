#!../venv/bin/python3
"""
this is business logic for validating json file
"""
import json
from flask import flash
from functions import utils
import os
from app import app

def validate_json(fileupload):
    """
    entry point for validating a given json file
    """
    if fileupload and utils.allowed_file(fileupload.filename,'ALLOWED_JSON_EXTENSIONS'):
        filetemploc = os.path.join(
            app.config['APP_PATH'], 'temp', fileupload.filename)
        fileloc = os.path.join(app.config['APP_PATH'], 'batchsubmitted', fileupload.filename)
        fileupload.save(filetemploc)
        feedback = validate_json_format(filetemploc)
        if not feedback:
            fileupload.seek(0)
            fileupload.save(fileloc)
            os.remove(filetemploc)
            return fileupload.filename
        else:
            for each in feedback:
                flash(each)
            os.remove(filetemploc)
            return False
    else:
        flash("Submit a json file")
        return False


def validate_json_format(fileloc):
    """
    specify conditions for json format
    """
    try:
        errorlist = []
        jsonobj = json.load(open(fileloc, 'r'))
        if jsonobj.get('subjects', False):
            for obj in jsonobj['subjects']:
                url = jsonobj['subjects'][obj].get("url", None)
                if url is None or url == '':
                    errorlist.append(str(obj) + " has no url field")
        return errorlist

    except Exception as loadexcept:
        errorlist.append("Problem opening json file.")
        # errorlist.append(loadexcept)
        return errorlist
