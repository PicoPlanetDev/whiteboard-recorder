import time
import subprocess
import cv2
import numpy as np
import os
import contextlib
import toml

TEMP_VIDEO_FILE = 'temp_video.mp4'
TEMP_AUDIO_FILE = 'temp_audio.mp3'
TEMP_PROCESSED_VIDEO_FILE = 'temp_processed_video.mp4'
OUTPUT_VIDEO_FILE = 'output_video.mp4'

def convert_to_jpeg(frame):
    ret, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()

def get_av_splits():
    # import shlex
    # shlex.split("ffmpeg -list_devices true -f dshow -i dummy")
    # Immediate exit requested, so stderr is used
    output = subprocess.run(['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy'],capture_output=True).stderr.decode('utf-8')

    return output.split('(video)')

class Configuration:
    def __init__(self):
        self.av_splits = get_av_splits()
        self.video_devices = self.get_video_devices()
        self.audio_devices = self.get_audio_devices()

        self.config = self.load_config()
        

    def get_video_devices(self):
        """Gets a list of video device names from the ffmpeg output.

        Returns:
            [str]: List of video device names.
        """        
        video_section = self.av_splits[:len(self.av_splits) - 1]

        # Since we split by (video), each video device is in a separate item
        video_devices = []
        for item in video_section:
            video_devices.append(item.split('"')[-2])

        video_devices_enumerated = [(str(i), name) for i, name in enumerate(video_devices)]

        return video_devices_enumerated

    def get_audio_devices(self):
        """Gets a list of audio device names from the ffmpeg output.

        Returns:
            [str]: List of audio device names.
        """     
        audio_section = self.av_splits[len(self.av_splits) - 1:]

        # len(audio_section) returns 1 so we just split by quotes
        audio_section_items = audio_section[0].split('"')
        # 3 7 11 seems to be counting by 4 starting at 3
        audio_devices = audio_section_items[3::4]

        audio_devices_enumerated = [(str(i), name) for i, name in enumerate(audio_devices)]

        return audio_devices_enumerated

    def load_config(self):
        try:
            with open('config.toml', 'r') as file:
                return toml.load(file)
        except FileNotFoundError:
            self.create_default_config()
            return self.load_config()

    def create_default_config(self):
        default_video_device = self.video_devices[0]
        default_audio_device = self.audio_devices[0]

        default_config = {
            'audio_device': default_audio_device,
            'video0': {
                'enabled': True,
                'video_device': default_video_device,
                'resolution': (1920, 1080),
                'corners': [(0, 0), (0, 0), (0, 0), (0, 0)]
            },
            'video1': {
                'enabled': False,
                'video_device': default_video_device,
                'resolution': (1920, 1080),
                'corners': [(0, 0), (0, 0), (0, 0), (0, 0)]
            }
        }
        self.config = default_config
        self.save_config()

    def save_config(self):
        with open('config.toml', 'w') as file:
            toml.dump(self.config, file)
    
    def get_all(self):
        all = {
            'video_devices': self.video_devices,
            'audio_devices': self.audio_devices,
            'audio_input_device': self.config['audio_device'],
            'video0': {
                'video_device': self.config['video0']['video_device'],
                'resolution': self.config['video0']['resolution'],
                'enabled': self.config['video0']['enabled']
            },
            # TODO: Add video2
            'video1': {
                'video_device': self.config['video1']['video_device'],
                'resolution': self.config['video1']['resolution'],
                'enabled': self.config['video1']['enabled']
            }
        }
        return all
    # TODO: work for both video1 and video2
    def update_all(self, data):
        self.config['audio_device'] = data['audio_input_device']
        self.config['video0']['video_device'] = data['video0']['video_device']
        self.config['video0']['resolution'] = data["video0"]["resolution"]
        self.config['video0']['enabled'] = data['video0']['enabled']
        self.config['video1']['video_device'] = data['video1']['video_device']
        self.config['video1']['resolution'] = data["video1"]["resolution"]
        self.config['video1']['enabled'] = data['video1']['enabled']
        self.save_config()


class VideoRecorder():
    def __init__(self, config):
        self.config = config

    def start_recording(self):
        # Get the configuration values
        video_device = self.config['video0']['video_device']
        audio_device = self.config['audio_device']
        input_resolution = self.config['video0']['resolution']

        # Start the recording process using ffmpeg
        self.recording_process = subprocess.Popen(
            ['ffmpeg', '-y', '-f', 'dshow', '-i', f'video={video_device}:audio={audio_device}', '-s', input_resolution,
             TEMP_VIDEO_FILE], stdin=subprocess.PIPE)

    def stop_recording(self):
        # Tell ffmpeg to stop recording
        self.recording_process.communicate(str.encode('q'))
        time.sleep(1)
        self.recording_process.terminate()

        # Extract the audio from the video
        subprocess.run(['ffmpeg', '-i', TEMP_VIDEO_FILE, '-y', '-codec:a', 'libmp3lame',
                        TEMP_AUDIO_FILE])

    def clear_files(self):
        with contextlib.suppress(FileNotFoundError):
            os.remove(TEMP_VIDEO_FILE)
            os.remove(TEMP_AUDIO_FILE)
            os.remove(TEMP_PROCESSED_VIDEO_FILE)
            os.remove(OUTPUT_VIDEO_FILE)


class Processing():
    def __init__(self, config):
        self.config = config

    def process_recording(self):
        video = cv2.VideoCapture(TEMP_VIDEO_FILE)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_file = cv2.VideoWriter(TEMP_PROCESSED_VIDEO_FILE, fourcc, 30.0, (1920, 1080))

        while video.isOpened():
            ret, frame = video.read()

            if not ret: break

            # Replace the frame with the birds eye view
            output = self.birds_eye_view(frame)
            out_file.write(output)

        video.release()
        out_file.release()

    def combine_video_and_audio(self):
        # Use ffmpeg to combine the new silent video with the audio from the original video
        subprocess.run(['ffmpeg', '-i', TEMP_AUDIO_FILE, '-i',
                        TEMP_PROCESSED_VIDEO_FILE, '-y', '-codec:a', 'copy', '-codec:v',
                        'copy', OUTPUT_VIDEO_FILE])
        print(f'Video saved to {OUTPUT_VIDEO_FILE}')

    def birds_eye_view(self, img):
        # Corners should be in this order
        # 0 1
        # 2 3

        # The problem right now is that the corners are rich from the aruco
        # but only points from the manual selection

        corners = self.config['video0']['corners']    

        init_corners = np.array(corners, dtype="float32")  # initial corners from the arguments
        dest_corners = np.array([[0, 0], [800, 0], [800, 800], [0, 800]],
                                dtype="float32")  # destination corners in a square

        # Compute the perspective transform matrix and then apply it
        transform_matrix = cv2.getPerspectiveTransform(init_corners, dest_corners)
        warped = cv2.warpPerspective(img, transform_matrix, (800, 800))
        resized = cv2.resize(warped, (1920, 1080))

        return resized
    
    def capture_frame(self, video_device=0):
        cap = cv2.VideoCapture(video_device, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.config['video0']['resolution'][0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.config['video0']['resolution'][1])
        while True:
            ret, frame = cap.read()
            if ret:
                cap.release()
                return frame