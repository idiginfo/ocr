#!../idiginfo/bin/python
"""
this is main business logic file
"""
import os
import subprocess
import requests
from businesslogic import cropthis, utils
from werkzeug import secure_filename
from flask import flash
from app import app


def tesseractthis(identifier, fileloc, cropit):
    """
    entry point for ocr file we have
    """
    outloc = app.config['OUTPUT_FOLDER'] + identifier
    outloc = os.path.abspath(outloc)
    if fileloc.endswith(".jpg"):
        if cropit == "top":
            cropthis.cropthis(fileloc, 0, 8)
        elif cropit == "left":
            cropthis.cropthis(fileloc, 15, 0)
        rtncode = subprocess.call(["tesseract", fileloc, outloc])
        if rtncode != 0:
            flash('Exception in OCR given file.')
            return False
        else:
            return open(outloc + ".txt", "rb").read().decode(
                'utf-8').replace("\n", " ")
    else:
        return "not a jpg file"


def tesseractinput(identifier, urlloc, fileupload, cropit):
    """
    entry point for business logic
    """
    try:
        filename = secure_filename(identifier + ".jpg")
        fileloc = os.path.abspath(
            os.path.join(app.config['UPLOAD_FOLDER'], filename))
        filehandler = open(fileloc, "wb")
        if not urlloc and (not fileupload or fileupload.filename == ''):
            flash('URL or File upload is required')
            return False
        elif fileupload and utils.allowed_file(fileupload.filename,'ALLOWED_EXTENSIONS'):
            fileupload.save(fileloc)
            return tesseractthis(identifier, fileloc, cropit)
        elif urlloc:
            try:
                resp = requests.get(urlloc)
                if resp.status_code == 200:
                    filehandler.write(resp.content)
                    filehandler.close()
                    return tesseractthis(identifier, fileloc, cropit)
                else:
                    flash('Image not found at given URL')
                    flash('Response code: ' + str(resp.status_code))
                    return False
            except:
                flash('Invalid URL')
                return False
        else:
            flash('Invalid input')
            return False
    except Exception as ex:
        flash('Something went wrong. Contact admin.')
        # +str(e)+traceback.format_exc())
        return False
