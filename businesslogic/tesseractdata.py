#!../idiginfo/bin/python
"""
this is main business logic file
"""
import os
import subprocess
import requests


def tesseractthis(identifier, fileloc):
    """
    entry point for ocr file we have
    """
    outloc = "ocrd/" + identifier
    outloc = os.path.abspath(outloc)
    if fileloc.endswith(".jpg"):
        subprocess.call(["tesseract",fileloc, outloc])
        return open(outloc + ".txt", "r").read().replace("\n"," ")
    else:
        return "not a jpg file"


def tesseractinput(identifier, url):
    """
    entry point for business logic
    """
    if os.path.isfile(url):
        return tesseractthis(identifier, url)
    else:
        fileloc = "images/" + identifier + ".jpg"
        fileloc = os.path.abspath(fileloc)
        filehandler = open(fileloc, "wb")
        filehandler.write(requests.get(url).content)
        filehandler.close()
        return tesseractthis(identifier, fileloc)
