from flask_cors import CORS
from werkzeug.utils import secure_filename
from flask import Flask, request, make_response, send_file, jsonify

import json

from details import get_email_details, get_sent_details

app = Flask(__name__)

@app.route('/check_inbox', methods=['POST'])
def check_inbox():
    email_details = get_email_details()
    return make_response(jsonify(email_details))

@app.route('/check_sent', methods=['POST'])
def check_sent():
    email_details = get_sent_details()
    return make_response(jsonify(email_details))

if __name__=='__main__':	
	app.run(port = 2000, host = '0.0.0.0')