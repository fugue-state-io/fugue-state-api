from . import process_audio
import os
from flask import Flask

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 1024 ** 4
    app.register_blueprint(process_audio.bp)
    
    return app