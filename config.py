"""
just a global location for app configurations
"""
import os

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
APP_LOC = '/data/web/ocr/'
OCR_STATUS = '/status/'
UPLOAD_FOLDER = '/data/web/ocr/images/'
OUTPUT_FOLDER = '/data/web/ocr/ocrd/'
LOG_FOLDER = '/data/web/ocr/ocrd/log/'
BATCHSUBMITED = '/data/web/ocr/batchsubmited'
BATCHINPROGRESS = '/data/web/ocr/batchinprogress'
BATCHPROCESSED = '/data/web/ocr/batchprocessed/'
TEMP = '/data/web/ocr/temp/'
ALLOWED_EXTENSIONS = ['jpg']
ALLOWED_JSON_EXTENSIONS = ['json']
DISALLOWED_JSON_FILENAME = ['inprogress.json', 'sampleformat.json']
DIRECTORY_LISTING = []
# get list of disallowed file names
ignore_list = ['.*']
for subdir, dirs, files in os.walk(BATCHSUBMITED):
    for file in files:

        DISALLOWED_JSON_FILENAME.append(file)
        DIRECTORY_LISTING.append(OCR_STATUS + file)
for subdir, dirs, files in os.walk(BATCHINPROGRESS):
    for file in files:

        DISALLOWED_JSON_FILENAME.append(file)
        DIRECTORY_LISTING.append(OCR_STATUS + file)
for subdir, dirs, files in os.walk(BATCHPROCESSED):
    for file in files:

        DISALLOWED_JSON_FILENAME.append(file)
        DIRECTORY_LISTING.append(OCR_STATUS + file)
PROPAGATE_EXCEPTIONS = True


def get(prop):
    """
    use this function to get one of the above property, when running
    outside flask, like batch processing in cron_tab
    """
    return eval(prop)
