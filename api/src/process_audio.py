import subprocess
import tempfile
import os
import wave
import pydub
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
                sound = pydub.AudioSegment.from_mp3(temp.name)
                sound.export(temp.name + '.wav', format='wav')
                # process = subprocess.Popen(['ffmpeg', '-i', temp.name, temp.name + '.wav'])
                # process.wait()
                signal_wave = wave.open(temp.name + '.wav', 'r')
                    #Extract Raw Audio from Wav File
                sample_rate = 16000
                sig = np.frombuffer(signal_wave.readframes(sample_rate), dtype=np.int16)
                plt.figure(1)

                plot_a = plt.subplot(211)
                plot_a.plot(sig)
                plot_a.set_xlabel('sample rate * time')
                plot_a.set_ylabel('energy')

                plot_b = plt.subplot(212)
                plot_b.specgram(sig, NFFT=1024, Fs=sample_rate, noverlap=900)
                plot_b.set_xlabel('Time')
                plot_b.set_ylabel('Frequency')
                tmpfile = BytesIO()
                
                plt.savefig(tmpfile)
                tmpfile.seek(0)
                if os.path.isfile(temp.name):
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