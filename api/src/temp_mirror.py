#!/usr/bin/python
from boto3 import session
import tempfile
import os
import logging
from flask import request, abort, jsonify, make_response, Blueprint, send_file
from flask_cors import cross_origin

bp = Blueprint("process_audio", __name__)
ALLOWED_EXTENSIONS = {'mp3', 'mp4', 'wav', 'flac'}

@bp.errorhandler(413)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)

# @bp.route('/temp_mirror', methods=['GET'])
# @cross_origin()
# def temp_retrieve():
#     logging.info({'route' : '/temp_mirror', 'info' : 'request headers ' + str(request.headers)})
#     if request.args.get("file"):
#         temp_sess = session.Session()
#         client = temp_sess.client('s3',
#                                 region_name='nyc3',
#                                 endpoint_url='https://nyc3.digitaloceanspaces.com',
#                                 aws_access_key_id=os.getenv("FUGUE_STATE_CDN_ACCESS_ID"),
#                                 aws_secret_access_key=os.getenv("FUGUE_STATE_CDN_SECRET_KEY"))
        
#         logging.info({'route' : '/temp_mirror', "info" : "upload_file running"})
#         get_object = client.get_object(Bucket="fugue-state-cdn", Key="temp/" + request.args.get("file"))
#         mimetype = None
#         if request.args.get("file").endswith(".mp4"):
#             mimetype = "video/mp4"
#         elif request.args.get("file").endswith(".mp3"):
#             mimetype = "audio/mpeg"
#         logging.info({'route' : '/temp_mirror', "info" : "get_object is %s" % get_object})
#         response = make_response(send_file(get_object['Body'], mimetype=mimetype, conditional=True))
#         response.headers["Accept-Ranges"] = "bytes"
#         return response
#     else:
#         logging.error({"route":"/temp_mirror", "error": request})
#         logging.error({"route":"/temp_mirror", "error": "file param not in request"})
#         abort(400)

@bp.route('/process_file', methods=['POST'])
@cross_origin()
def process_file():
    logging.info({'route' : '/process_file', 'info' : 'request headers ' + str(request.headers)})
    logging.info({"route" : "/process_file", "info" : request.content_type})
    file_suffix = None
    if request.content_type == "audio/mpeg":
        file_suffix = ".mp3"
    elif request.content_type == "video/mp4":
        file_suffix = ".mp4"
    if request.data and file_suffix:
        
        logging.info({'route' : '/process_file', "info" : "create temporary file"})
        request_file = request.data
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write(request_file)
        temp_sess = session.Session()
        client = temp_sess.client('s3',
                                region_name='nyc3',
                                endpoint_url='https://nyc3.digitaloceanspaces.com',
                                aws_access_key_id=os.getenv("FUGUE_STATE_CDN_ACCESS_ID"),
                                aws_secret_access_key=os.getenv("FUGUE_STATE_CDN_SECRET_KEY"))
        
        logging.info({'route' : '/process_file', "info" : "upload_file running"})
        client.upload_file(temp_file.name, 'fugue-state-cdn', 'temp/' + temp_file.name.split("/")[-1] + file_suffix)
        logging.info({"route" : "/process_file", "info" : "returning presigned url"})
        return make_response(jsonify({"url" : client.generate_presigned_url("get_object", {"Bucket": 'fugue-state-cdn', "Key": 'temp/' + temp_file.name.split("/")[-1] + file_suffix})}))

    else:
        logging.error({"route":"/process_file", "error": request})
        logging.error({"route":"/process_file", "error": request.files})
        logging.error({"route":"/process_file", "error": "file not in request"})
        abort(400)