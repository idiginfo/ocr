"""
just a global location for app configurations
"""
import os
from dotenv import load_dotenv
load_dotenv()

APP_PATH = os.getenv('APP_PATH')
LOG_PATH = os.getenv('LOG_PATH')
WTF_CSRF_ENABLED = os.getenv('WTF_CSRF_ENABLED')
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_EXTENSIONS = ['jpg']
ALLOWED_JSON_EXTENSIONS = ['json']
DISALLOWED_JSON_FILENAME = ['inprogress.json', 'sampleformat.json']
DIRECTORY_LISTING = []

# get list of disallowed file names
ignore_list = ['.*']
for subdir, dirs, files in os.walk(os.path.join(APP_PATH, 'batchsubmitted')):
    for file in files:
        if file.endswith(('.json')):
            DISALLOWED_JSON_FILENAME.append(file)
            DIRECTORY_LISTING.append('/status/' + file)
for subdir, dirs, files in os.walk(os.path.join(APP_PATH, 'batchinprogress')):
    for file in files:
        if file.endswith(('.json')):
            DISALLOWED_JSON_FILENAME.append(file)
            DIRECTORY_LISTING.append('/status/' + file)
for subdir, dirs, files in os.walk(os.path.join(APP_PATH, 'batchprocessed')):
    for file in files:
        if file.endswith(('.json')):
            DISALLOWED_JSON_FILENAME.append(file)
            DIRECTORY_LISTING.append('/status/' + file)
PROPAGATE_EXCEPTIONS = True


def get(prop):
    """
    use this function to get one of the above property, when running
    outside flask, like batch processing in cron_tab
    """
    return eval(prop)
