from flask import Flask

webapp = Flask(__name__)
webapp.secret_key = '\x80\xa9s*\x12\xc7x\xa9d\x1f(\x03\xbeHJ:\x9f\xf0!\xb1a\xaa\x0f\xee'

from app import route_sample
from app import file_uploader
from app import account_managment

