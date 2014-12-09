"""
just a global location for app configurations
"""
WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
APP_LOC = '/home/shiva/Desktop/ocr/idiginfo-ocr/'
# APP_LOC = '/home/si13f/idiginfo-ocr/'
UPLOAD_FOLDER = '/home/shiva/Desktop/ocr/idiginfo-ocr/images/'
OUTPUT_FOLDER = '/home/shiva/Desktop/ocr/idiginfo-ocr/ocrd/'
BATCHSUBMITED = '/home/shiva/Desktop/ocr/idiginfo-ocr/batchsubmited/'
BATCHPROCESSED = '/home/shiva/Desktop/ocr/idiginfo-ocr/batchprocessed/'
TEMP = '/home/shiva/Desktop/ocr/idiginfo-ocr/temp/'
# TEMP = '/home/si13f/idiginfo-ocr/temp/'
# UPLOAD_FOLDER = '/home/si13f/idiginfo-ocr/images/'
# OUTPUT_FOLDER = '/home/si13f/idiginfo-ocr/ocrd/'
# BATCHSUBMITED = '/home/si13f/idiginfo-ocr/batchsubmited/'
# BATCHPROCESSED = '/home/si13f/idiginfo-ocr/batchprocessed/'
ALLOWED_EXTENSIONS = set(['jpg'])
ALLOWED_JSON_EXTENSIONS = set(['json'])
DISALLOWED_JSON_FILENAME = set(['inprogress.json', 'sampleformat.json'])
PROPAGATE_EXCEPTIONS = True


def get(prop):
    """
    use this function to get one of the above property, when running
    outside flask, like batch processing in cron_tab
    """
    return eval(prop)
