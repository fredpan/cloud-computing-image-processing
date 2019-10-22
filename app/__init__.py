from flask import Flask, session

webapp = Flask(__name__)
webapp.secret_key = '\x80\xa9s*\x12\xc7x\xa9d\x1f(\x03\xbeHJ:\x9f\xf0!\xb1a\xaa\x0f\xee'

from app import RouteMapper
from app import FileUploader
from app import AccountManagment
from app.api import Apis

# set the max size of img allowed
webapp.config['MAX_CONTENT_LENGTH'] = 1024*1024*5

@webapp.before_request
def make_session_permanent():
    session.permanent = True