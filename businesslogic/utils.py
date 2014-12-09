#!../idiginfo/bin/python
"""
this is where all utils hold
"""
# from app import app


def allowed_file(filename,type):
    """
    this functions returns true if extension of
    file name is in allowed json extension set
    from config.py
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in get_property(type)


def get_property(prop):
    """
    just a wrapper for config get property
    """
    import config
    return config.get(prop)