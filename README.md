# Whiteboard Recorder

## A recording system that creates a birds-eye view of a whiteboard recorded from any perspective

## Branch webapp

Replaces the prior Flask-hosted static site with a Vue and Flask webapp. Information below may be incorrect.

![Screenshot of the homepage of Whiteboard Recorder](https://raw.githubusercontent.com/PicoPlanetDev/whiteboard-recorder/webapp/screenshots/homepage.png)

## Requirements

- Python 3
- Virtual environment with packages installed in `requirements.txt`: `opencv-python,flask,numpy,qrcode,flask_cors,toml`
- FFmpeg
  - On Windows: `ffmpeg.exe` in the `whiteboard-recorder/backend` directory
  - On Linux: `sudo apt install ffmpeg`

### Reccomended hardware

- A capable computer with the software requirements installed
- A webcam with a decently high resolution (preferably 1920x1080 or better)
- A microphone
- (Optional) A USB cable extender rated for the USB version that the camera communicates with, to mount the camera far from the computer

## Installation

1. Use `git clone https://github.com/PicoPlanetDev/whiteboard-recorder` to download the source code
2. `cd whiteboard-recorder` then
3. Switch to the `webapp` branch using `git switch webapp`
4. `cd frontend` then `npm install`
5. `cd ../backend` then create a virtual environment `venv` in the backend directory
    a. On Windows: `python -m venv venv` and activate the venv with `.\venv\Scripts\activate`
    b. On Linux: `python3 -m venv venv` and activate the venv with `source venv/bin/activate`
6. Install the required packages
  a. On Windows: `pip install -r requirements.txt`
  b. On Linux: `pip3 install -r requirements.txt`

## Usage

This will be updated once the built webapp is released and I make a simple start script, but in the meantime, just use the dev servers as follows:

1. `cd` into the `whiteboard-recorder` directory
2. Create a second terminal emulator tab/window in the same directory
3. In the first terminal: `cd frontend` then `npm run dev -- --host`
4. In the second terminal: `cd backend` then
  a. On Windows: `.\venv\Scripts\activate` then `python app.py`
  b. On Linux: `source venv/bin/activate` then `python3 app.py`
5. Navigate in a modern browser to `http://localhost:5173`
  a. To control Whiteboard Recorder from another device, replace `localhost` with the host computer's local IP address
6. Select **Settings** in the navbar and select your microphone and camera(s), then setup their respective parameters as necessary.
  a. On Linux, it is necessary to manually enter the audio and video devices. Use `arecord -L` to see the available audio inputs, and `v4l2-ctl --list-devices` to see available video devices
7. Configure the bird's eye perspective warp using the **Launch video configurator** button:
  a. Select the video device you want to set up
  b. Click **Capture frame** to get an image for reference
  c. Click the top left corner of the whiteboard
  d. Select the colored arrow button for the top right corner, then click the image again to set that corner
  e. Repeat this process for the two remaining corners
  f. Click **Save** then **Preview warped**
  g. Make any changes you need and save again, repeat the process for another camera, or close the dialog and continue
8. Return to the root page by selecting **Home** in the navbar, then begin a recording with the **Start recording** button
9. End the recording by clicking the **Stop recording** button.
10. The recording is processed automatically, then will be available by clicking the **Download recording** button.
