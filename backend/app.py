from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
import socket  # Get local IP address
import os
import qrcode
import io
import base64
import subprocess
# my modules
import configuration
import processing
import jobs
import recorder
import aruco

# Flask setup
app = Flask(__name__)
app.secret_key = 'secret'
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

config = configuration.Configuration()
preview = processing.Preview(config)
job_manager = jobs.JobManager(config, preview)
video_recorder = recorder.VideoRecorder(config)

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
            job_manager.start_recording()
            is_recording = True
        # if not recording and request to stop recording (something went wrong)
        if not new_recording_status:
            return jsonify({'status': "error", 'recording_status': is_recording})

    if is_recording:
        # if recording and request to stop recording
        if not new_recording_status:
            is_recording = False
            job_manager.stop_recording()

        # if recording and request to start recording (something went wrong)
        if new_recording_status:
            return jsonify({'status': "error", 'recording_status': is_recording})
    
    return jsonify({'status': "success", 'recording_status': is_recording})

# Download recording video (if exists)
@app.route('/api/download_recording', methods=['GET'])
def download():
    global config
    output_file = config.config['files']['output_video_file']
    if os.path.isfile(output_file):
        return send_file(output_file, as_attachment=True)
    else:
        # notify no file
        print("no file")
        return jsonify({'status': "error"})

# Gets the local IP address of the machine running the backend
def get_local_ip():
    # attempt to get tailscale ip address
    result = subprocess.check_output(['tailscale', 'ip']).decode("utf-8")
    if "command not found" not in result:
        ip = result.split()[0]
        return ip

    # otherwise, get local ip address
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

@app.route('/api/get_local_ip', methods=['GET'])
def get_ip():
    return jsonify({'ip': get_local_ip()})

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
        except Exception as e:
            print(e)
            return jsonify({'status': "error", 'message': str(e)})
        return jsonify({'status': "success"})

    elif request.method == 'GET': # fetch settings
        # get settings
        return jsonify(config.get_all())

@app.route('/api/capture_frame', methods=['POST'])
def capture_frame():
    video_device = request.get_json()['video_device']
    global preview
    # focus the camera
    global video_recorder
    video_recorder.focus_camera(video_device)
    frame_jpeg = processing.convert_to_jpeg(preview.capture_frame(video_device))
    return "data:image/jpg;base64," + base64.b64encode(frame_jpeg).decode('utf-8')

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
    video_device = request.get_json()['video_device']
    global preview
    frame_jpeg = processing.convert_to_jpeg(preview.warp_frame(video_device))
    return "data:image/jpg;base64," + base64.b64encode(frame_jpeg).decode('utf-8')

@app.route('/api/jobs', methods=['GET', 'POST'])
def jobs_route():
    global job_manager
    # Refreshing the jobs list
    if request.method == 'GET':
        return jsonify({"jobs": job_manager.get_all_jobs()})
    elif request.method == 'POST':
        data = request.get_json()
        # Figure out what action to perform
        match data['action']:
            case 'run':
                job_manager.run_job(data['job_name'])
                return jsonify({'status': "success"})
            case 'remove':
                job_manager.remove_job(data['job_name'])
                return jsonify({'status': "success"})
            case 'download':
                global config
                output_file = job_manager.get_job_output_file(data['job_name'])
                return send_file(output_file, as_attachment=True)
            case 'run_all':
                job_manager.run_jobs()
                return jsonify({'status': "success"})
            case 'clear_finished':
                job_manager.clear_finished_jobs()
                return jsonify({'status': "success"})

@app.route('/api/purge_recordings_directory', methods=['POST'])
def purge_recordings():
    global job_manager
    job_manager.purge_recording_directory()
    return jsonify({'status': "success"})

@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    if request.get_json()['type'] == 'restart':
        if os.name == 'nt':
            os.system("shutdown /r /t 1")
        elif os.name == 'posix':
            os.system("systemctl reboot")
        else:
            return jsonify({'status': "error", 'message': "OS not supported"})
        return jsonify({'status': "success"})
    
    elif request.get_json()['type'] == 'shutdown':
        if os.name == 'nt':
            os.system("shutdown /s /t 1") # not sure if this works withouth admin privileges
        elif os.name == 'posix':
            os.system("systemctl poweroff") # need systemd
        else:
            return jsonify({'status': "error", 'message': "OS not supported"})
        return jsonify({'status': "success"})

@app.route('/api/update', methods=['POST'])
def update():
    # This is a sketchy way to update the backend
    os.system("git stash && git fetch && git pull && git stash pop && sudo systemctl restart whiteboard-recorder-backend.service")
    return jsonify({'status': "success"})

@app.route('/api/detect_aruco_corners', methods=['POST'])
def detect_aruco_corners():
    video_device = request.get_json()['video_device']
    global config
    global preview
    frame = preview.capture_frame(video_device)
    if frame is None: return jsonify({'status': "error", 'message': "Failed to capture frame"})

    try: aruco.set_video_corners(video_device, frame, config)
    except Exception as e: return jsonify({'status': "error", 'message': str(e)})

    return jsonify({'status': "success"})

@app.route('/api/preview_aruco_corners', methods=['POST'])
def preview_aruco_corners():
    video_device = request.get_json()['video_device']
    global config
    global preview
    frame = preview.capture_frame(video_device)
    if frame is None: return jsonify({'status': "error", 'message': "Failed to capture frame"})

    debug_frame = aruco.set_video_corners(video_device, frame, config)
    frame_jpeg = processing.convert_to_jpeg(debug_frame)
    return "data:image/jpg;base64," + base64.b64encode(frame_jpeg).decode('utf-8')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)