import time
import subprocess
import cv2
import numpy as np
import os
import contextlib
import toml

TEMP_VIDEO_FILES = ['temp_video_0.mp4', 'temp_video_1.mp4']
TEMP_AUDIO_FILE = 'temp_audio.mp3'
TEMP_PROCESSED_VIDEO_FILE = 'temp_processed_video.mp4'

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
        if os.name == 'nt':
            self.av_splits = get_av_splits()
            self.video_devices = self.get_video_devices()
            self.audio_devices = self.get_audio_devices()
        elif os.name == 'posix':
            # Must be entered manually
            self.av_splits = []
            self.video_devices = [[0, '/dev/video0']] # an actual thing
            self.audio_devices = [[0, 'default']] # Not an actual thing
        else:
            raise Exception('OS not supported')

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
        default_video_device = [str(self.video_devices[0][0]),str(self.video_devices[0][1])]
        default_audio_device = [str(self.audio_devices[0][0]),str(self.audio_devices[0][1])]

        default_config = {
            'audio_device': default_audio_device,
            'custom_audio_device_card': '',
            'custom_audio_device_dev': '',
            'video0': {
                'enabled': True,
                'video_device': default_video_device,
                'resolution': (1920, 1080),
                'corners': [(0, 0), (0, 0), (0, 0), (0, 0)],
                'custom_video_device': "",
                'custom_video_device_index': -1
            },
            'video1': {
                'enabled': False,
                'video_device': default_video_device,
                'resolution': (1920, 1080),
                'corners': [(0, 0), (0, 0), (0, 0), (0, 0)],
                'custom_video_device': "",
                'custom_video_device_index': -1
            },
            'output_video_file': 'output_video.mp4'
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
            'custom_audio_device_card': self.config['custom_audio_device_card'],
            'custom_audio_device_dev': self.config['custom_audio_device_dev'],
            'video0': {
                'video_device': self.config['video0']['video_device'],
                'resolution': self.config['video0']['resolution'],
                'enabled': self.config['video0']['enabled'],
                'custom_video_device': self.config['video0']['custom_video_device'],
                'custom_video_device_index': self.config['video0']['custom_video_device_index'],
            },
            # TODO: Add video2
            'video1': {
                'video_device': self.config['video1']['video_device'],
                'resolution': self.config['video1']['resolution'],
                'enabled': self.config['video1']['enabled'],
                'custom_video_device': self.config['video1']['custom_video_device'],
                'custom_video_device_index': self.config['video1']['custom_video_device_index'],
            },
            'output_video_file': self.config['output_video_file']
        }
        return all
    
    # TODO: work for both video1 and video2
    def update_all(self, data):
        # Audio is global
        self.config['audio_device'] = data['audio_input_device']
        self.config['custom_audio_device_card'] = data['custom_audio_device_card']
        self.config['custom_audio_device_dev'] = str(data['custom_audio_device_dev'])
        # Video 0 options
        self.config['video0']['video_device'] = data['video0']['video_device']
        self.config['video0']['resolution'] = data["video0"]["resolution"]
        self.config['video0']['enabled'] = data['video0']['enabled']
        self.config['video0']['custom_video_device'] = data['video0']['custom_video_device']
        self.config['video0']['custom_video_device_index'] = data['video0']['custom_video_device_index']
        # Video 1 options
        self.config['video1']['video_device'] = data['video1']['video_device']
        self.config['video1']['resolution'] = data["video1"]["resolution"]
        self.config['video1']['enabled'] = data['video1']['enabled']
        self.config['video1']['custom_video_device'] = data['video0']['custom_video_device']
        self.config['video1']['custom_video_device_index'] = data['video0']['custom_video_device_index']

        self.save_config()

    def get_video_device_index(self, video_device):
        if self.config['video'+str(video_device)]["custom_video_device_index"] != -1:
            return self.config['video'+str(video_device)]["custom_video_device_index"]
        else:
            return int(self.config['video'+str(video_device)]["video_device"][0])
        
    def get_video_device_name(self, video_device):
        if self.config['video'+str(video_device)]["custom_video_device"] != "":
            return self.config['video'+str(video_device)]["custom_video_device"]
        else:
            return self.config['video'+str(video_device)]["video_device"][1]


class VideoRecorder():
    def __init__(self, config, video_device_index=0):
        self.config = config
        self.video_device_index = video_device_index
        self.recording_process = None

    def start_recording(self):
        # Get the video device config string
        video_device_config = 'video'+str(self.video_device_index)

        # Get the configuration values
        video_device = self.config.get_video_device_name(self.video_device_index)
        audio_device = self.config.config['audio_device'][1]
        input_resolution = f"{self.config.config[video_device_config]['resolution'][0]}x{self.config.config[video_device_config]['resolution'][1]}"

        # Start the recording process using ffmpeg
        # self.recording_process = subprocess.Popen(
        #     ['ffmpeg', '-y', '-f', 'dshow', '-video_size', input_resolution, '-pixel_format', 'yuyv422', '-i', f'video={video_device}:audio={audio_device}', 
        #      TEMP_VIDEO_FILES[self.video_device_index]], stdin=subprocess.PIPE)
        
        # Obviously this is not gonna fly on linux
        if os.name == 'nt':
            self.recording_process = subprocess.Popen(
                ['ffmpeg','-y','-f','dshow','-vcodec','mjpeg','-video_size',input_resolution,'-i',f'video={video_device}:audio={audio_device}',TEMP_VIDEO_FILES[self.video_device_index]], stdin=subprocess.PIPE)
        elif os.name == 'posix':
            # Put together the custom audio device string
            linux_audio_device = f'hw:CARD={self.config.config["custom_audio_device_card"]}'
            if self.config.config['custom_audio_device_dev'] != '':
                linux_audio_device += f',DEV={self.config.config["custom_audio_device_dev"]}'
            # Start the recording process using ffmpeg
            self.recording_process = subprocess.Popen(
                ['ffmpeg','-y','-f','v4l2','-framerate','30','-video_size',input_resolution,'-i',f'{video_device}','-f','alsa','-ac','2','-i',linux_audio_device,TEMP_VIDEO_FILES[self.video_device_index]], stdin=subprocess.PIPE)
        else:
            raise Exception('OS not supported')


    def stop_recording(self):
        # Tell ffmpeg to stop recording
        self.recording_process.communicate(str.encode('q'))
        time.sleep(1)
        self.recording_process.terminate()

        # Extract the audio from the video
        subprocess.run(['ffmpeg', '-i', TEMP_VIDEO_FILES[self.video_device_index], '-y', '-codec:a', 'libmp3lame',
                        TEMP_AUDIO_FILE])

    def clear_files(self):
        with contextlib.suppress(FileNotFoundError): # Ignore if the file doesn't exist (likely)
            os.remove(TEMP_VIDEO_FILES[self.video_device_index])
            os.remove(TEMP_AUDIO_FILE)
            os.remove(TEMP_PROCESSED_VIDEO_FILE)
            os.remove(self.config.config['output_video_file'])


class Processing():
    def __init__(self, config):
        self.config = config

    def process_recording(self, video_device_index=0):
        video = cv2.VideoCapture(TEMP_VIDEO_FILES[video_device_index])

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
        output_filename = self.config.config['output_video_file']
        # Use ffmpeg to combine the new silent video with the audio from the original video
        subprocess.run(['ffmpeg', '-i', TEMP_AUDIO_FILE, '-i',
                        TEMP_PROCESSED_VIDEO_FILE, '-y', '-codec:a', 'copy', '-codec:v',
                        'copy', output_filename])
        print('Video saved to ' + output_filename)

    def birds_eye_view(self, img, video_device=0):
        # Corners should be in this order
        # 0 1
        # 2 3

        # The problem right now is that the corners are rich from the aruco
        # but only points from the manual selection

        corners = self.config.config['video'+str(video_device)]['corners']
        # Make a copy of the corners
        corners = corners.copy()
        corners[2], corners[3] = corners[3], corners[2]

        init_corners = np.array(corners, dtype="float32")  # initial corners from the arguments
        dest_corners = np.array([[0, 0], [1000, 0], [1000, 1000], [0, 1000]],
                                dtype="float32")  # destination corners in a square

        # Compute the perspective transform matrix and then apply it
        transform_matrix = cv2.getPerspectiveTransform(init_corners, dest_corners)
        warped = cv2.warpPerspective(img, transform_matrix, (1000, 1000))

        # Debug:
        # for corner in corners:
        #     img = cv2.circle(img, corner, 10, (0, 0, 255), -1)
        resized = cv2.resize(warped, (1920, 1080))

        return resized
    
class Preview():
    def __init__(self, config, processing):
        self.config = config
        self.frame = None
        self.processing = Processing(config)

    def capture_frame(self, video_device=0):
        video_device_config = 'video'+str(video_device)

        if os.name == 'nt':
            cap = cv2.VideoCapture(video_device, cv2.CAP_DSHOW) # remove CAP_DSHOW if you want to use the default camera driver, slower to start?
        else:
            cap = cv2.VideoCapture(self.config.get_video_device_index(video_device))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.config[video_device_config]['resolution'][0]) # set the X resolution
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.config[video_device_config]['resolution'][1]) # set the Y resolution
        while True:
            ret, frame = cap.read()
            if ret:
                cap.release()
                self.frame = frame
                return frame
            
    def warp_frame(self):
        # Debug
        # warped_frame = self.frame
        # for corner in self.config.config['video'+str(video_device)]['corners']:
        #     warped_frame = cv2.circle(self.frame, corner, 10, (0, 0, 255), -1)
        return self.processing.birds_eye_view(self.frame)