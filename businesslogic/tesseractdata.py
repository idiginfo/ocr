#!../idiginfo/bin/python
"""
this is main business logic file
"""
import os
import subprocess
import requests
from businesslogic import cropthis


def tesseractthis(identifier, fileloc,cropit):
    """
    entry point for ocr file we have
    """
    outloc = "ocrd/" + identifier
    outloc = os.path.abspath(outloc)
    if fileloc.endswith(".jpg"):
        if cropit == "top":
            cropthis.cropthis(fileloc,0,8)
        elif cropit == "left":
            cropthis.cropthis(fileloc,15,0)
        subprocess.call(["tesseract",fileloc, outloc])
        return open(outloc + ".txt", "r").read().replace("\n"," ")
    else:
        return "not a jpg file"


def tesseractinput(identifier, url,cropit):
    """
    entry point for business logic
    """
    fileloc = "images/" + identifier + ".jpg"
    fileloc = os.path.abspath(fileloc)
    filehandler = open(fileloc, "wb")
    if os.path.isfile(url):
        filehandler.write(open(url,"rb").read())
        filehandler.close()
    else:
        filehandler.write(requests.get(url).content)
        filehandler.close()
    return tesseractthis(identifier, fileloc,cropit)
