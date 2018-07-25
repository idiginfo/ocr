"""
sample form classcan be used if
you want to simply add a form
with identifier and url fields
Not using it anyway
"""

from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired


class OcrForm(Form):

    """
    form class
    """

    def __init__(self):
        pass
    identifier = StringField('id', validators=[DataRequired()])
    url = StringField('url')
