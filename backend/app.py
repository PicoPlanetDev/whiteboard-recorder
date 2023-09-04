from flask import Flask, send_file, jsonify
from flask_cors import CORS
import socket  # Get local IP address
import recorder
import os
import qrcode
import io

app = Flask(__name__)
app.secret_key = 'secret'

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# recorder
config = recorder.Configuration()
video_recorder = recorder.VideoRecorder(config)

is_recording = False

# CYA
@app.route('/api')
def index():
    return f"Reached the backend, go to {get_local_ip()}:5173 to use Whiteboard Recorder"

@app.route('/api/start_recording', methods=['POST'])
def record():
    global is_recording
    if not is_recording:
        video_recorder.clear_files()
        video_recorder.start_recording()
        is_recording = True
        # notify recording
        print("recording")
    else:
        # notify already recording
        print("already recording")
    return jsonify({'status': "success"})


@app.route('/api/stop_recording', methods=['POST'])
def stop():
    global is_recording
    if is_recording:
        is_recording = False
        video_recorder.stop_recording()
        processing = recorder.Processing(config)
        # notify processing
        print("processing recording")
    else:
        # notify not recording
        print("not recording")
    return jsonify({'status': "success"})


@app.route('/api/download_recording', methods=['GET'])
def download():
    output_file = config.get_value('output_video_file')
    if os.path.isfile(output_file):
        return send_file(output_file, as_attachment=True)
    else:
        # notify no file
        print("no file")
        return jsonify({'status': "error"})

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('1.1.1.1', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

@app.route('/api/get_qr_code', methods=['GET'])
def create_url_qr_code():
    qr = qrcode.make(f'http://{get_local_ip()}:5173')
    buf = io.BytesIO()
    qr.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype="image/jpeg")

@app.route('/api/recording_status', methods=['GET'])
def recording_status():
    global is_recording
    return jsonify({'recording_status': is_recording})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)