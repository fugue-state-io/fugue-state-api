from . import process_audio
import os
from flask import Flask

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = (1024 ** 2) * 50
app.register_blueprint(process_audio.bp)