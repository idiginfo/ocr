from flask import render_template, flash, redirect, request, jsonify
from app import app
from .forms import OcrForm

@app.route('/')
@app.route('/index')
def index():
    form = OcrForm()
    return render_template("index.html",form=form,)

@app.route('/ocr', methods=['GET', 'POST'])
def ocr():
    form = OcrForm()
    if form.validate_on_submit():
        from businesslogic import tesseractdata
        ocrvalue = tesseractdata.tesseractinput(form.identifier.data,form.url.data)
        # bagofwords = " ".join([x for x in ocrvalue.split(" ") if len(x)>2 and len(x)<15])
        if request.form['response'] == "html":
            return render_template("ocr.html",form=form,ocrvalue=ocrvalue)
        else:
            outvalue = {'identifier':form.identifier.data,'ocr':ocrvalue}
            return jsonify(outvalue)
    return render_template('index.html', 
                           form=form,)
