#!../idiginfo/bin/python
"""
this is where all utils hold
"""
from app import app
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_JSON_EXTENSIONS']