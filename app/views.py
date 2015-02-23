"""
This is place where you define all URL types application can be accessed with
"""

from flask import render_template, flash, request, redirect
from flask import jsonify, session, get_flashed_messages, abort
from app import app
from businesslogic import jsonvalidator, tesseractdata
import json
import os


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
    resp = request.args.get('response', 0)
    if fileupload is None or fileupload.filename == '':
        flash('require a json file to start batch ocr')
        return abort(400) if resp else render_template("batch.html")
    if fileupload.filename in app.config['DISALLOWED_JSON_FILENAME']:
        flash("Cannot accept this file name. File name already exist."
              "Please change your file name and resubmit.")
        return abort(400) if resp else render_template("batch.html")
    else:
        app.config['DISALLOWED_JSON_FILENAME'].append(fileupload.filename)
        app.config['DIRECTORY_LISTING'].append(
            app.config['OCR_STATUS'] + fileupload.filename)
    feedback = jsonvalidator.validate_json(fileupload)
    if feedback:
        iden = "http://ocr.dev.morphbank.net/status/" + feedback
        return render_template(
            '202.html', iden=iden, filename=feedback), 202 if resp else\
            render_template('batchocroutput.html', iden=iden,
                            filename=feedback)
    else:
        return abort(202) if resp else render_template("batch.html")


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
    filepath = os.path.join(app.config['BATCHPROCESSED'], filename)
    filealtpath = os.path.join(app.config['BATCHSUBMITED'], filename)
    if os.path.isfile(filepath):
        return jsonify(json.load(open(filepath, 'r')))
    elif os.path.isfile(filealtpath):
        return jsonify(json.load(open(filealtpath, 'r')))
    else:
        abort(404)


@app.route('/status', methods=['GET', 'POST'])
def directorylisting():
    """
    route for directory listing and status form
    """
    iden = request.form.get('file name')
    if iden is not None:
        return redirect("/status/" + iden)
    return render_template("status.html",
                           displayfiles=app.config['DIRECTORY_LISTING'])
