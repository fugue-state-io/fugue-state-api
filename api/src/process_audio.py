import tempfile
import os
import wave
import pydub
import base64
import logging

import numpy as np
import matplotlib.figure as figure

from io import BytesIO
from werkzeug.utils import secure_filename
from flask import request, abort, Blueprint, make_response, jsonify

bp = Blueprint("process_audio", __name__)
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def mp3_to_wave(file, temp):
    temp.write(file.read())
    sound = pydub.AudioSegment.from_mp3(temp.name)
    sound.export(temp.name + '.wav', format='wav')
    return  wave.open(temp.name + '.wav', 'r')

def wave_to_bytes(signal_wave):
    sample_rate = -1
    sig = np.frombuffer(signal_wave.readframes(sample_rate), dtype=np.int16)
    fig = figure.Figure()
    plot_a = fig.subplots()
    plot_a.plot(sig, color="g", linewidth=0.25)
    plot_a.axis('off')
    tmpfile = BytesIO()
    fig.savefig(tmpfile, bbox_inches='tight', pad_inches = 0, transparent=True, dpi=256)
    tmpfile.seek(0)
    return tmpfile.read()

@bp.errorhandler(413)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)

@bp.route('/api/process_audio', methods=['POST'])
def process_audio():
    logging.info({"route":"/api/process_audio"})
    if 'file' in request.files:
        logging.info({"route":"/api/process_audio request", "info" : "file exists"})
        file = request.files['file']
        if file and allowed_file(file.filename):
            logging.info({"route":"/api/process_audio request", "info" : "file allowed"})
            filename = secure_filename(file.filename)
            if filename.split('.')[1] != 'wav':
                logging.info({"route":"/api/process_audio request", "info" : ".mp3 file provided"})
                temp = tempfile.NamedTemporaryFile()
                signal_wave = mp3_to_wave(file, temp)
                logging.info({"route":"/api/process_audio request", "info" : ".mp3 converted to wave"})
                data = wave_to_bytes(signal_wave)
                logging.info({"route":"/api/process_audio request", "info" : "wav file to bytes"})
                if os.path.isfile(temp.name + '.wav'):
                    os.remove(temp.name + '.wav')
                    logging.info({"route":"/api/process_audio request", "info" : "cleaned up wav file"})
                data = base64.b64encode(data).decode()
                logging.info({"route":"/api/process_audio request", "info" : "base64 encoded data"})
                return f'data:image/png;base64,{data}'

            return 'File uploaded successfully'
        else:
            abort(400)

    abort(400)