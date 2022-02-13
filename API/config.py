import os
#This gives us the root directory for the project
basedir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Config(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    API_DOMAIN = 'http://127.0.0.1:5000'

