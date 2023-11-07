from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
import socket  # Get local IP address
import os
import qrcode
import io
import base64
# my modules
import recorder
import configuration
import processing

# Flask setup
app = Flask(__name__)
app.secret_key = 'secret'
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

config = configuration.Configuration()
video_recorder = recorder.VideoRecorder(config)
video_processing = processing.Processing(config)
preview = processing.Preview(config, video_processing)

is_recording = False # nasty global variable

# Remind the user to go to the frontend if they go to the backend
@app.route('/api')
def index():
    return f"Reached the backend, go to {get_local_ip()}:5173 to use Whiteboard Recorder"

@app.route('/api/toggle_recording', methods=['POST'])
def toggle_recording():
    """Starts or stops recording based on the request data"""

    new_recording_status = request.get_json()['recording_status'] # Determine whether to start or stop recording

    global is_recording
    if not is_recording:
        # if not recording and request to start recording
        if new_recording_status:
            video_recorder.clear_files()
            video_recorder.start_recording()
            is_recording = True
        # if not recording and request to stop recording (something went wrong)
        if not new_recording_status:
            return jsonify({'status': "error", 'recording_status': is_recording})
    # if recording and request to stop recording
    if is_recording:
        # if recording and request to stop recording
        if not new_recording_status:
            video_recorder.stop_recording()
            is_recording = False
            global video_processing
            video_processing.process_recording()
            video_processing.combine_video_and_audio()
        # if recording and request to start recording (something went wrong)
        if new_recording_status:
            return jsonify({'status': "error", 'recording_status': is_recording})
    
    return jsonify({'status': "success", 'recording_status': is_recording})

# Download recording video (if exists)
@app.route('/api/download_recording', methods=['GET'])
def download():
    global config
    output_file = config.config['output_video_file']
    if os.path.isfile(output_file):
        return send_file(output_file, as_attachment=True)
    else:
        # notify no file
        print("no file")
        return jsonify({'status': "error"})

# Gets the local IP address of the machine running the backend
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

# Gets a QR code for the frontend URL
@app.route('/api/get_qr_code', methods=['GET'])
def create_url_qr_code():
    qr = qrcode.make(f'http://{get_local_ip()}:5173')
    buf = io.BytesIO()
    qr.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype="image/jpeg")

# Returns whether or not the backend is recording
@app.route('/api/recording_status', methods=['GET'])
def recording_status():
    global is_recording
    return jsonify({'recording_status': is_recording})

# Returns the current settings
@app.route('/api/settings', methods=['GET','POST'])
def settings():
    global config
    if request.method == 'POST': # update settings
        # update settings
        request_data = request.get_json()
        try:
            config.update_all(request_data)
        except TypeError as e:
            print(e)
            return jsonify({'status': "error", 'message': str(e)})
        return jsonify({'status': "success"})

    elif request.method == 'GET': # fetch settings
        # get settings
        return jsonify(config.get_all())

@app.route('/api/capture_frame', methods=['POST'])
def capture_frame():
    video_device = int(request.get_json()['video_device'])
    global preview
    frame_jpeg = recorder.convert_to_jpeg(preview.capture_frame(video_device))
    return "data:image/png;base64," + base64.b64encode(frame_jpeg).decode('utf-8')

@app.route('/api/corners', methods=['GET','POST'])
def corners():
    global config
    if request.method == 'POST':
        # update settings
        request_data = request.get_json()
        video_device = request_data['video_device']

        # Validate the request
        if not isinstance(request_data, dict):
            return jsonify({'status': "error", 'message': "request_data must be a dictionary"})
        if not isinstance(video_device, str):
            return jsonify({'status': "error", 'message': "video_device must be a string"})
        if video_device not in config.config:
            return jsonify({'status': "error", 'message': "Given video_device not present in config"})
        if 'corners' not in request_data:
            return jsonify({'status': "error", 'message': "Missing corners in request_data"})
        
        corners = request_data['corners']
        # Convert the corners to ints
        for corner in corners:
            corner[0] = int(corner[0])
            corner[1] = int(corner[1])

        config.config[video_device]['corners'] = corners
        config.save_config()

        return jsonify({'status': "success"})

    # shouldn't be used yet
    elif request.method == 'GET':
        # get settings
        corner_dict = {
            'video0': config.config['video0']['corners'],
            'video1': config.config['video1']['corners']
        }
        return jsonify(corner_dict)
    
@app.route('/api/preview_warped', methods=['POST'])
def preview_warped():
    #video_device = int(request.get_json()['video_device'])
    global preview
    frame_jpeg = recorder.convert_to_jpeg(preview.warp_frame())
    return "data:image/png;base64," + base64.b64encode(frame_jpeg).decode('utf-8')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)