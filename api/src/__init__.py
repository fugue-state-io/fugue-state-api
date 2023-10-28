import os
import sys
import logging
from flask import Flask
from flask_cors import CORS

from . import process_audio, readiness
logging.basicConfig(stream=sys.stdout, encoding='utf-8', level=logging.INFO)
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = (1024 ** 2) * 50
app.register_blueprint(process_audio.bp)
app.register_blueprint(readiness.bp)
CORS(app)
