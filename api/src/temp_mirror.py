#!/usr/bin/python
from boto3 import session
import tempfile
import os
import logging
from flask import request, abort, jsonify, make_response, Blueprint

bp = Blueprint("process_audio", __name__)
ALLOWED_EXTENSIONS = {'mp3', 'mp4', 'wav', 'flac'}

@bp.errorhandler(413)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)

@bp.route('/temp_mirror', methods=['POST'])
def temp_mirror():
    logging.info({'route' : '/temp_mirror'})
    if 'file' in request.files:
        
        logging.info({'route' : '/temp_mirror', "info" : "create temporary file"})
        request_file = request.files['file']
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write(request_file.read())
        temp_sess = session.Session()
        client = temp_sess.client('s3',
                                region_name='nyc3',
                                endpoint_url='https://nyc3.digitaloceanspaces.com',
                                aws_access_key_id=os.getenv("FUGUE_STATE_CDN_ACCESS_ID"),
                                aws_secret_access_key=os.getenv("FUGUE_STATE_CDN_SECRET_KEY"))
        
        logging.info({'route' : '/temp_mirror', "info" : "upload_file running"})
        client.upload_file(temp_file.name, 'fugue-state-cdn', 'temp/' + temp_file.name.split("/")[-1])
        logging.info({"route" : "/temp_mirror", "info" : "return presigned url"})
        return make_response(jsonify({"url" : client.generate_presigned_url("get_object", {"Bucket": 'fugue-state-cdn', "Key": 'temp/' + temp_file.name.split("/")[-1]})}))
    else:
        logging.error({"route":"/temp_mirror", "error": "file not in request"})
        abort(400)