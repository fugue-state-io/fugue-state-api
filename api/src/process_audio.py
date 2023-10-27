import subprocess
import tempfile
import os
import wave
import pydub
import numpy as np
import matplotlib.figure as figure
import uuid
from io import BytesIO
from werkzeug.utils import secure_filename
from flask import Flask, send_file, request, abort, Blueprint, make_response, jsonify
bp = Blueprint("process_audio", __name__)
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
@bp.errorhandler(413)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)

@bp.route('/api/process_audio', methods=['POST'])
def process_audio():
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if filename.split('.')[1] != 'wav':
                temp = tempfile.NamedTemporaryFile()
                temp.write(file.read())
                sound = pydub.AudioSegment.from_mp3(temp.name)
                sound.export(temp.name + '.wav', format='wav')
                signal_wave = wave.open(temp.name + '.wav', 'r')
                sample_rate = -1
                sig = np.frombuffer(signal_wave.readframes(sample_rate), dtype=np.int16)
                fig = figure.Figure()

                plot_a = fig.subplots()
                plot_a.plot(sig, color="g", linewidth=0.25)
                plot_a.axis('off')
                
                tmpfile = BytesIO()
                
                fig.savefig(tmpfile, bbox_inches='tight', pad_inches = 0, transparent=True, dpi=256)

                tmpfile.seek(0)
                if os.path.isfile(temp.name + '.wav'):
                    os.remove(temp.name + '.wav')
                return send_file(
                    tmpfile,
                    as_attachment=True,
                    download_name=filename.split('.')[0] + '.png',
                    mimetype='image/png'
                )
            return 'File uploaded successfully'
        else:
            abort(400)

    abort(400)