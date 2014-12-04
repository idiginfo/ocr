from flask import render_template, flash, redirect, request, jsonify, session, get_flashed_messages
from app import app
from .forms import OcrForm

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/ocr')
def index():
    return render_template("ocrsinglefile.html")

@app.route('/ocroutput', methods=['GET', 'POST'])
def ocr():
    from businesslogic import tesseractdata
    iden = request.form.get('identifier')
    if iden is None: iden = request.args.get('identifier')
    urlloc = request.form.get('url')  # .data
    if urlloc is None: urlloc = request.args.get('url')
    # return jsonify({'iden':iden,'urloc':urlloc})
    fileupload = request.files.get('file',None)
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
           
    session.pop('_flashes',None)
    return jsonify(outvalue)
    # return render_template('ocrsinglefile.html', 
    #               form=form,)

@app.route('/batchoutput', methods=['GET', 'POST'])
def batchocr():
    id = "http://www.example.com"
    return render_template('confirmbatch.html', id=id)
    
@app.route('/batch')
def batch():
    return render_template("batch.html")
