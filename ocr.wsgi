#import os
#import sys

##virtual env settings
#activate_this = '/data/web/ocr/idiginfo/bin/activate_this.py'
#exec(open(activate_this).read())
#activate_this = '/data/web/ocr/idiginfo/bin/activate_this.py'
#execfile(activate_this, dict(__file__=activate_this))

#sys.path.insert(0, '/data/web/ocr/idiginfo/*')
#sys.path.append('/home/si13f/idiginfo-ocr/app/')
#sys.path.append('/home/si13f/idiginfo-ocr/idiginfo/*')

#sys.stdout = sys.stderr
from app import app as application
