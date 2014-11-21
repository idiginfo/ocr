from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class OcrForm(Form):
    identifier = StringField('id', validators=[DataRequired()])
    url = StringField('url')
    

