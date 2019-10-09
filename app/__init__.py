from flask import Flask

webapp = Flask(__name__)

from app import route_sample
from app import file_uploader

