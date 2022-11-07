from flask import Flask, render_template, redirect, url_for, flash, Markup, send_file
import socket  # Get local IP address
import recorder
import os
import qrcode

app = Flask(__name__)
app.secret_key = 'secret'

# recorder
config = recorder.Configuration()
video_recorder = recorder.VideoRecorder(config)

is_recording = False

@app.route('/')
def index():
    create_url_qr_code()
    return render_template(
        'index.html',
        ip_address=get_local_ip()
    )


@app.route('/start', methods=['GET'])
def record():
    global is_recording
    if not is_recording:
        video_recorder.clear_files()
        video_recorder.start_recording()
        flash(Markup('<div class="alert alert-success" role="alert">Recording started</div>'))
        is_recording = True
    else:
        flash(Markup('<div class="alert alert-warning" role="alert">Already recording</div>'))
    return redirect(url_for('index'))


@app.route('/stop', methods=['GET'])
def stop():
    global is_recording
    if is_recording:
        is_recording = False
        video_recorder.stop_recording()
        processing = recorder.Processing(config)
        flash(Markup('<div class="alert alert-danger" role="alert">Recording ended</div>'))
    else:
        flash(Markup('<div class="alert alert-warning" role="alert">Not recording</div>'))
    return redirect(url_for('index'))


@app.route('/download', methods=['GET'])
def download():
    output_file = config.get_value('output_video_file')
    if os.path.isfile(output_file):
        return send_file(output_file, as_attachment=True)
    else:
        flash(Markup(
            '<div class="alert alert-warning" role="alert">No recording to download. Maybe it\'s still processing.</div>'))
        return redirect(url_for('index'))


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


def create_url_qr_code():
    qr = qrcode.make(f'http://{get_local_ip()}:5000')
    qr.save('static/qr/qr.png')


if __name__ == '__main__':
    if config.get_value('ip') != get_local_ip():
        config.set_value('ip', get_local_ip())
        create_url_qr_code()

    app.run(debug=False, host='0.0.0.0', port=5000)