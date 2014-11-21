#!../idiginfo/bin/python
"""
this is business logic for cropping file
"""
import subprocess
import os


def cropthis(imageloc, xval, yval):
    """
    entry point for croping an image
    """
    try:
        dirname = os.path.dirname(imageloc)
        filename = os.path.basename(imageloc).split(".")
        oldfilename = os.path.join(
            dirname, filename[0] + "_old." + filename[1])
        oldfiledata = open(imageloc, 'rb').read()
        open(oldfilename, 'wb').write(oldfiledata)
        dimfile = os.path.join(dirname, filename[0] + ".txt")
        subprocess.call(['convert', imageloc, '-format', '"%h %w"', 'info:'],
                        stdout=open(dimfile, 'w'))
        dim = open(dimfile, 'r').read().strip().replace('"', '').split(" ")
        percentx = (xval / 100) * int(dim[0])
        percenty = (yval / 100) * int(dim[1])
#         rtnval = subprocess.call(['convert', oldfilename, '-crop',
#                                   '+{0}+{1}'.format(percentx, percenty),'-brightness-contrast', '0x50',imageloc])
        rtnval = subprocess.call(['convert', oldfilename, '-crop',
                                  '+{0}+{1}'.format(percentx, percenty),'-level', '50x100%',imageloc])
#         rtnval = subprocess.call(['convert', oldfilename, '-crop',
#                                   '+{0}+{1}'.format(percentx, percenty),imageloc])
        if rtnval != 0:
            return False
        else:
            return True
    except Exception as cropthis_exception:
        print(cropthis_exception)
        return False
