"""
This is place where you define all URL types application can be accessed with
"""

from flask import render_template, flash, request, redirect, Response
from flask import jsonify, session, get_flashed_messages, abort
from app import app
from functions import jsonvalidator, tesseractdata
import json
import sys
import os
import traceback
import requests
import psutil
from os import path


@app.route('/')
@app.route('/home')
def home():
    """
    defining url for home
    """
    return render_template('home.html')


@app.route('/ocr')
def index():
    """
    defining url for ocr tab
    """
    return render_template("ocrsinglefile.html")


@app.route('/ocroutput', methods=['GET', 'POST'])
def ocr():
    """
    defining url for ocr output
    """
    iden = request.form.get('identifier')
    if iden is None:
        iden = request.args.get('identifier')
    urlloc = request.form.get('url')  # .data
    if urlloc is None:
        urlloc = request.args.get('url')
    # return jsonify({'iden':iden,'urloc':urlloc})
    fileupload = request.files.get('file', None)
    # return jsonify({'iden':iden,'urloc':urlloc,'fileupload':fileupload})
    cropit = request.form.get('crop')
    if cropit is None:
        cropit = request.args.get('crop')
    ocrvalue = tesseractdata.tesseractinput(iden, urlloc, fileupload, cropit)
    response = request.form.get('response')
    if response is None:
        response = request.args.get('response')
    if response == "html":
        if not ocrvalue:
            return render_template('ocrsinglefile.html')
        else:
            return render_template("ocrsinglefileoutput.html",
                                   iden=iden, url=urlloc, ocrvalue=ocrvalue)
    else:
        flaskmessages = get_flashed_messages()
        if not ocrvalue:
            outvalue = {
                'identifier': iden, 'ocr': 'error', 'messages': flaskmessages}
        else:
            outvalue = {'identifier': iden, 'ocr':
                        ocrvalue, 'messages': flaskmessages}

    session.pop('_flashes', None)
    return jsonify(outvalue)
    # return render_template('ocrsinglefile.html',
    #               form=form,)


@app.route('/batchocr', methods=['GET', 'POST'])
def batchocr():
    """
    defining url for batch ocr submission
    """
    fileupload = request.files.get('file', None)
    resp = request.form.get('response')
    if resp is None:
        resp = request.args.get('response')
    if fileupload is None or fileupload.filename == '':
        flash('require a json file to start batch ocr')
        return (render_template('400.html'), 400)\
            if resp else render_template("batch.html")
    if fileupload.filename in app.config['DISALLOWED_JSON_FILENAME']:
        flash("Cannot accept this file name. File name already exist."
              "Please change your file name and resubmit.")
        return (render_template('400.html'), 400)\
            if resp else render_template("batch.html")
    else:
        app.config['DISALLOWED_JSON_FILENAME'].append(fileupload.filename)
        app.config['DIRECTORY_LISTING'].append('/status/' + fileupload.filename)
    feedback = jsonvalidator.validate_json(fileupload)
    if feedback:
        iden = "http://ocr.dev.morphbank.net/status/" + feedback
        return (render_template(
            '202.html', iden=iden, filename=feedback), 202) if resp else\
            render_template('batchocroutput.html', iden=iden,
                            filename=feedback)
    else:
        return (render_template(
            '202.html'), 202) if resp else render_template("batch.html")


@app.route('/batch')
def batch():
    """
    defining url for batch ocr welcome page
    """
    return render_template("batch.html")


@app.route('/status/<filename>', methods=['GET', 'POST'])
def status(filename):
    """
    defining url for status page
    """
    filepath = os.path.join(app.config['APP_PATH'], 'batchprocessed', filename)
    fileinprogresspath = os.path.join(app.config['APP_PATH'], 'batchinprogress', filename)
    filealtpath = os.path.join(app.config['APP_PATH'], 'batchsubmitted', filename)
    if os.path.isfile(filepath):
        return jsonify(json.load(open(filepath, 'r')))
    elif os.path.isfile(filealtpath):
        return jsonify(json.load(open(filealtpath, 'r')))
    elif os.path.isfile(fileinprogresspath):
        return jsonify(json.load(open(fileinprogresspath, 'r')))
    else:
        abort(404)

@app.route('/status', methods=['GET', 'POST'])
def directorylisting():
    """
    route for directory listing and status form
    """
    iden = request.form.get('file name')
    if iden is not None:
        return redirect('/status/' + iden)
    return render_template("status.html",
                           displayfiles=app.config['DIRECTORY_LISTING'])


def requires_auth(function_to_decorate):
    """
    authentication wrapper using an apikey
    """
    def wrapper(*args, **kw):
        """
        takes care of generating 401 if required
        """
        apikey = request.headers.get('API-KEY', 0)
        if apikey:
            if apikey == 't$p480UAJ5v8P=ifcE23&hpM?#+&r3':
                return function_to_decorate(*args, **kw)
        abort(401)
    return wrapper


@app.route('/delete', methods=['GET', 'POST'])
@requires_auth
def delete_file(*args, **kwargs):
    """
    responsible for deleting a file from server
    """
    filename = request.form.get('file')
    if filename is None:
        filename = request.args.get('file')
    if filename:
        filesubmited = os.path.join(app.config['APP_PATH'], 'batchsubmitted', filename)
        fileprocessed = os.path.join(app.config['APP_PATH'], 'batchprocessed', filename)
        fileinprogress = os.path.join(app.config['APP_PATH'], 'batchinprogress', filename)
        if(os.path.isfile(filesubmited)):
            filealtpath = filesubmited
        elif(os.path.isfile(fileprocessed)):
            filealtpath = fileprocessed
        elif(os.path.isfile(fileinprogress)):
            filealtpath = fileinprogress
        try:
            app.config['DISALLOWED_JSON_FILENAME'].remove(filename)
            app.config['DIRECTORY_LISTING'].remove('/status/' + filename)
            os.remove(filealtpath)
        except OSError:
            pass
        except ValueError:
            pass
    return Response('successfully deleted file', 200)
