import tempfile
import os
import wave
import pydub
import base64
import logging
import imghdr
from PIL import Image
import numpy as np
import matplotlib.figure as figure

from io import BytesIO
from werkzeug.utils import secure_filename
from flask import request, abort, Blueprint, make_response, jsonify

bp = Blueprint("process_audio", __name__)
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac'}
def readable_resolution(size: tuple):
    return str(size[0]) + 'x' + str(size[1])


def is_valid_image_file(file_path: str):
    file_type = imghdr.what(file_path)
    return file_type == 'png'


def is_pixel_alpha(pixel: tuple or int):
    pixel_value = pixel[3] if isinstance(pixel, tuple) else pixel
    return pixel_value == 0
def crop(bytes):

    image = Image.open(bytes, 'r')
    width = image.size[0]
    height = image.size[1]
    pixels = image.load()

    top = 0
    bottom = 0
    left = 0
    right = 0

    for y in range(0, height):
        for x in range(0, width):
            if not is_pixel_alpha(pixels[x, y]):
                if left == 0 or x - 1 < left:
                    left = x - 1
                break

    for y in range(0, height):
        for x in range(0, width):
            if not is_pixel_alpha(pixels[x, y]):
                if top == 0 or y < top:
                    top = y
                break

    for y in reversed(range(0, height)):
        for x in reversed(range(0, width)):
            if not is_pixel_alpha(pixels[x, y]):
                if right == 0 or x + 1 > right:
                    right = x + 1
                break

    for y in reversed(range(0, height)):
        for x in reversed(range(0, width)):
            if not is_pixel_alpha(pixels[x, y]):
                if bottom == 0 or y + 1 > bottom:
                    bottom = y + 1
                break

    if left == -1:
        left = 0

    if top == -1:
        top = 0

    if right == 0:
        right = width

    if bottom == 0:
        bottom = height

    cropped_image = image.crop((left, top, right, bottom))
    image.close()
    buffered = BytesIO()
    cropped_image.save(buffered, format="png")
    return buffered.getvalue()

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
    plot_a.plot(sig, color="g", linewidth=0.1)
    plot_a.axis('off')
    tmpfile = BytesIO()
    fig.savefig(tmpfile, bbox_inches='tight', pad_inches = 0, transparent=True, dpi=256)
    tmpfile.seek(0)
    return tmpfile

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
                data = crop(wave_to_bytes(signal_wave))
                logging.info({"route":"/api/process_audio", "info" : "wav file to bytes"})
                if os.path.isfile(temp.name + '.wav'):
                    os.remove(temp.name + '.wav')
                    logging.info({"route":"/api/process_audio", "info" : "cleaned up wav file"})
                data = base64.b64encode(data).decode()
                logging.info({"route":"/api/process_audio", "info" : "base64 encoded data"})
                return f'data:image/png;base64,{data}'

            return 'File uploaded successfully'
        else:
            abort(400)

    abort(400)