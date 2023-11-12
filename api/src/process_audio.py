import tempfile
import os
import wave
import pydub
import base64
import logging
import imghdr
import png
from PIL import Image
import numpy as np
import matplotlib.figure as figure

from io import BytesIO
from werkzeug.utils import secure_filename
from flask import request, abort, Blueprint, make_response, jsonify

bp = Blueprint("process_audio", __name__)
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac'}


def is_valid_image_file(file_path: str):
    file_type = imghdr.what(file_path)
    return file_type == 'png'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def mp3_to_wave(file, temp):
    temp.write(file.read())
    sound = pydub.AudioSegment.from_mp3(temp.name)
    sound.export(temp.name + '.wav', format='wav')
    return  wave.open(temp.name + '.wav', 'r')

def wave_to_normalised_float(signal_wave):
    sample_rate = -1
    sig = np.frombuffer(signal_wave.readframes(sample_rate), dtype=np.int16)
    audio_as_np_float32 = sig.astype(np.float32)

    # Normalise float32 array so that values are between -1.0 and +1.0                                                      
    max_int16 = 2**15
    audio_normalised = audio_as_np_float32 / max_int16
    return audio_normalised

def floats_to_png(floats):
    height = 2
    width = 2048
    floats_per_width = round(len(floats) / width)
    f = bytearray()
    for y in range(height):
        for x in range(width):
            f.append(round(min(floats[x * floats_per_width + y: x * floats_per_width + floats_per_width: 2]) * 128) + 128)
            f.append(round(max(floats[x * floats_per_width + y: x * floats_per_width + floats_per_width: 2]) * 128) + 128)


    return f

@bp.errorhandler(413)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)

@bp.route('/api/process_audio', methods=['POST'])
def process_audio():
    logging.info({"route":"/api/process_audio"})
    if 'file' in request.files:
        logging.info({"route":"/api/process_audio", "info" : "file exists"})
        file = request.files['file']
        if file and allowed_file(file.filename):
            logging.info({"route":"/api/process_audio", "info" : "file allowed"})
            filename = secure_filename(file.filename)
            if filename.split('.')[1] != 'wav':
                logging.info({"route":"/api/process_audio", "info" : ".mp3 file provided"})
                temp = tempfile.NamedTemporaryFile()
                signal_wave = mp3_to_wave(file, temp)
                logging.info({"route":"/api/process_audio", "info" : ".mp3 converted to wave"})
                floats = wave_to_normalised_float(signal_wave)
                data = floats_to_png(floats)
                logging.info({"route":"/api/process_audio", "info" : "wav file to bytes"})
                if os.path.isfile(temp.name + '.wav'):
                    os.remove(temp.name + '.wav')
                    logging.info({"route":"/api/process_audio", "info" : "cleaned up wav file"})
                data = base64.b64encode(data).decode()
                logging.info({"route":"/api/process_audio", "info" : "base64 encoded data"})
                return f'{data}'

            return 'File uploaded successfully'
        else:
            abort(400)
    
    logging.error({"route":"/api/process_audio", "error": "file not in request"})
    abort(400)