from flask import render_template, flash, redirect, request, jsonify, session, get_flashed_messages, url_for, abort
from app import app
from .forms import OcrForm
from businesslogic import jsonvalidator, tesseractdata
import json
import os

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/ocr')
def index():
    return render_template("ocrsinglefile.html")

@app.route('/ocroutput', methods=['GET', 'POST'])
def ocr():
    iden = request.form.get('identifier')
    if iden is None: iden = request.args.get('identifier')
    urlloc = request.form.get('url')  # .data
    if urlloc is None: urlloc = request.args.get('url')
    # return jsonify({'iden':iden,'urloc':urlloc})
    fileupload = request.files.get('file', None)
    # return jsonify({'iden':iden,'urloc':urlloc,'fileupload':fileupload})
    cropit = request.form.get('crop')
    if cropit is None: cropit = request.args.get('crop')
    ocrvalue = tesseractdata.tesseractinput(iden, urlloc, fileupload, cropit)
    response = request.form.get('response')
    if response is None: response = request.args.get('response')
    if response == "html":
        if not ocrvalue:
            return render_template('ocrsinglefile.html')
        else:
            return render_template("ocrsinglefileoutput.html", iden=iden, url=urlloc, ocrvalue=ocrvalue)
    else:
        flaskmessages = get_flashed_messages()
        if not ocrvalue:
            outvalue = {'identifier':iden, 'ocr':'error', 'messages':flaskmessages}
        else:
            outvalue = {'identifier':iden, 'ocr':ocrvalue, 'messages':flaskmessages}
           
    session.pop('_flashes', None)
    return jsonify(outvalue)
    # return render_template('ocrsinglefile.html', 
    #               form=form,)

@app.route('/batchocr', methods=['GET', 'POST'])
def batchocr():
    fileupload = request.files.get('file', None)
    if fileupload is None or fileupload.filename=='':
        flash('require a json file to start batch ocr')
        return render_template("batch.html")
    feedback = jsonvalidator.validate_json(fileupload)
    if feedback:
        id = "http://ocr.dev.morphbank.net/status/"+feedback
        return render_template('batchocroutput.html', id=id,filename=feedback)
    else:
        return render_template("batch.html")
    
@app.route('/batch')
def batch():
    return render_template("batch.html")

@app.route('/status/<filename>', methods=['GET', 'POST'])
def status(filename):
    filepath = os.path.join(app.config['BATCHPROCESSED'],filename)
    filealtpath = os.path.join(app.config['BATCHSUBMITED'],filename)
    if os.path.isfile(filepath):
        return jsonify(json.load(open(filepath,'r')))
    elif os.path.isfile(filealtpath):
        return jsonify(json.load(open(filealtpath,'r')))
    else:
        abort(404)
    