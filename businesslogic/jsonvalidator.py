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
    """
    entry point for validating a given json file
    """
    if fileupload and utils.allowed_file(fileupload.filename,'ALLOWED_JSON_EXTENSIONS'):
        filetemploc = os.path.join(
            app.config['TEMP'], fileupload.filename)
        fileloc = os.path.join(
            app.config['BATCHSUBMITED'], fileupload.filename)
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
        if jsonobj.get('list', False):
            for obj in jsonobj['list']:
                url = jsonobj['list'][obj].get("url", None)
                if url is None or url == '':
                    errorlist.append(str(obj) + " has no url field")
        return errorlist

    except Exception as loadexcept:
        errorlist.append("Problem opening json file.")
        # errorlist.append(loadexcept)
        return errorlist
