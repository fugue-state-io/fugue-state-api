from flask import Blueprint, make_response, jsonify
bp = Blueprint("readiness", __name__)

@bp.route('/', methods=['GET'])
def readiness():
    return make_response(jsonify({'status' : 'good'}), 200)