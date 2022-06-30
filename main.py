## USE PYTHON 3.7
## AMT WILL NOT WORK ON HIGHER VERSION

import os
import asyncio
from flask_sock import Sock
import create_midi

from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
sockets = Sock(app)

HTTP_SERVER_PORT = 5000

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/transcribe', methods=['GET'])
def ReturnJSON():
    if request.method == 'GET':
        data = {
            "Kidnap" : 'Influencer',
            "Subject" : "Post Toilet Bowl for me",
        }

        return jsonify(data)

@app.route('/api/references', methods=['GET'])
def get_reference_list():
    ref_path = './reference_midi'
    ref_list = [file_name[:-4] for file_name in os.listdir(ref_path)]

    data = {
        'reference_files': ref_list
    }

    return jsonify(data)

# api endpoint for mobile app to send audio bytes to
# accepts POST requests with JSON data
# if audio is missing, returns "fuck off"
# data:
#
# audio: bytes
# 
@app.route('/api/transcribe', methods=['POST'])
def transcribe_endpoint():
    # check for JSON content type
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        # get JSON and if it has audio bytes - process it
        json = request.json
        if 'audio' in json:
            # transcribe audio (this is a placeholder)
            user_midi_file_name = create_midi.transcribe_from_string(json['audio'])

            # compare to reference and get error dict
            # convert output dictionary to json and respond to app
            if 'reference' in json:
                data = create_midi.extract_errors(user_midi_file_name, reference_midi_file_name=json['reference']+'.mid')
                return jsonify(data)
            # if no reference is provided, use the test file
            data = create_midi.extract_errors(user_midi_file_name, reference_midi_file_name="reference_1octave_up.mid")
            return jsonify(data)


    # else (any error) -> return fuck off
    data = { 'fuck':'off' }
    return jsonify(data)

if __name__=="__main__":
    loop = asyncio.get_event_loop()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0')

