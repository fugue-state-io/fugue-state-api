import subprocess
import tempfile
import os
import wave
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from werkzeug.utils import secure_filename
from flask import Flask, send_file, request, abort, Blueprint
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
                process = subprocess.Popen(['ffmpeg', '-i', temp.name, temp.name + '.wav'])
                process.wait()
                signal_wave = wave.open(temp.name + '.wav', 'r')
                if os.path.isfile(temp.name):
                    os.remove(temp.name + '.wav')
                sample_rate = 16000
                sig = np.frombuffer(signal_wave.readframes(sample_rate), dtype=np.int16)
                plt.figure(1)

                plot_a = plt.subplot(211)
                plot_a.plot(sig)
                tmpfile = BytesIO()
                plt.savefig(tmpfile, format="png")
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