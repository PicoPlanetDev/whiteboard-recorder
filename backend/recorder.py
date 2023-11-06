import time
import subprocess
import cv2
import numpy as np
import os
import contextlib
import toml
import time

TEMP_VIDEO_FILES = ['temp_video_0.mkv', 'temp_video_1.mkv']
TEMP_AUDIO_FILE = 'temp_audio.mp3'
TEMP_PROCESSED_VIDEO_FILE = 'temp_processed_video.mp4'

def convert_to_jpeg(frame: np.ndarray):
    """Converts an OpenCV image to a jpeg

    Args:
        frame (np.ndarray): The OpenCV image

    Returns:
        bytes: The jpeg encoded bytes of the image
    """    
    ret, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()

def get_av_splits():
    """Gets the output of ffmpeg list_devices splits it into video and audio sections"""
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
            'end_recording_delay': 1,
            'video0': {
                'enabled': True,
                'video_device': default_video_device,
                'resolution': (1920, 1080),
                'corners': [(0, 0), (0, 0), (0, 0), (0, 0)],
                'custom_video_device': "",
                'custom_video_device_index': -1,
                'streamcopy': False,
                'framerate': 30,
                'input_format': 'mjpeg',
            },
            'video1': {
                'enabled': False,
                'video_device': default_video_device,
                'resolution': (1920, 1080),
                'corners': [(0, 0), (0, 0), (0, 0), (0, 0)],
                'custom_video_device': "",
                'custom_video_device_index': -1,
                'streamcopy': False,
                'framerate': 30,
                'input_format': 'mjpeg',
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
            'end_recording_delay': self.config['end_recording_delay'],
            'video0': {
                'video_device': self.config['video0']['video_device'],
                'resolution': self.config['video0']['resolution'],
                'enabled': self.config['video0']['enabled'],
                'custom_video_device': self.config['video0']['custom_video_device'],
                'custom_video_device_index': self.config['video0']['custom_video_device_index'],
                'streamcopy': self.config['video0']['streamcopy'],
                'framerate': self.config['video0']['framerate'],
                'input_format': self.config['video0']['input_format'],
            },
            'video1': {
                'video_device': self.config['video1']['video_device'],
                'resolution': self.config['video1']['resolution'],
                'enabled': self.config['video1']['enabled'],
                'custom_video_device': self.config['video1']['custom_video_device'],
                'custom_video_device_index': self.config['video1']['custom_video_device_index'],
                'streamcopy': self.config['video1']['streamcopy'],
                'framerate': self.config['video1']['framerate'],
                'input_format': self.config['video1']['input_format'],
            },
            'output_video_file': self.config['output_video_file']
        }
        return all
    
    def update_all(self, data):
        # Validate data itself
        if not isinstance(data, dict):
            raise TypeError('Expected data to be a dict')
        
        # Validate audio_input_device
        if not isinstance(data['audio_input_device'], list):
            raise TypeError("Expected audio_input_device to be a 2D enumerated list")
        self.config['audio_input_device'] = [str(i) for i in data['audio_input_device']]

        # Validate custom_audio_device_card
        if not isinstance(data['custom_audio_device_card'], str):
            raise TypeError("Expected custom_audio_device_card to be a string")
        self.config['custom_audio_device_card'] = data['custom_audio_device_card']

        # Validate custom_audio_device_dev
        if not isinstance(data['custom_audio_device_dev'], (int, str)):
            raise TypeError("Expected custom_audio_device_dev to be an int or string")
        self.config['custom_audio_device_dev'] = str(data['custom_audio_device_dev'])

        # Validate end_recording_delay
        if not isinstance(data['end_recording_delay'], (int, float)):
            raise TypeError("Expected end_recording_delay to be a number")
        self.config['end_recording_delay'] = data['end_recording_delay']

        # Validate video0 and video1
        for video in ['video0', 'video1']:
            if not isinstance(data[video], dict):
                raise TypeError(f"Expected {video} to be a dictionary")

            # Validate video_device
            if not isinstance(data[video]['video_device'], list):
                raise TypeError(f"Expected {video}['video_device'] to be a list")
            self.config[video]['video_device'] = [str(i) for i in data[video]['video_device']]

            # Validate the resolution
            if not isinstance(data[video]['resolution'], (list, tuple)):
                raise TypeError(f"Expected {video}['resolution'] to be a list or tuple")
            if len(data[video]['resolution']) != 2:
                raise TypeError(f"Expected {video}['resolution'] to be a list or tuple of length 2")
            for i in data[video]['resolution']:
                if not isinstance(i, int):
                    raise TypeError(f"Expected {video}['resolution'] to be a list or tuple of ints")
            self.config[video]['resolution'] = data[video]['resolution']

            # Validate enabled
            if not isinstance(data[video]['enabled'], bool):
                raise TypeError(f"Expected {video}['enabled'] to be a bool")
            self.config[video]['enabled'] = data[video]['enabled']

            # Validate custom_video_device
            if not isinstance(data[video]['custom_video_device'], str):
                raise TypeError(f"Expected {video}['custom_video_device'] to be a string")
            self.config[video]['custom_video_device'] = data[video]['custom_video_device']

            # Validate custom_video_device_index
            if not isinstance(data[video]['custom_video_device_index'], int):
                raise TypeError(f"Expected {video}['custom_video_device_index'] to be an int")
            self.config[video]['custom_video_device_index'] = data[video]['custom_video_device_index']

            # Validate streamcopy
            if not isinstance(data[video]['streamcopy'], bool):
                raise TypeError(f"Expected {video}['streamcopy'] to be a bool")
            self.config[video]['streamcopy'] = data[video]['streamcopy']

            # Validate framerate
            if not isinstance(data[video]['framerate'], int):
                raise TypeError(f"Expected {video}['framerate'] to be an int")
            self.config[video]['framerate'] = data[video]['framerate']

            # Validate input_format
            if not isinstance(data[video]['input_format'], str):
                raise TypeError(f"Expected {video}['input_format'] to be a string")
            self.config[video]['input_format'] = data[video]['input_format']

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
        video_device_config = self.config.config['video'+str(self.video_device_index)]

        # Get the configuration values that will be reused
        video_device = self.config.get_video_device_name(self.video_device_index)
        audio_device = self.config.config['audio_device'][1] # specifically the audio device name
        input_resolution = f"{video_device_config['resolution'][0]}x{video_device_config['resolution'][1]}"
        input_format = video_device_config['input_format']
        recording_file = TEMP_VIDEO_FILES[self.video_device_index]
        framerate = str(video_device_config["framerate"])

        # Put together the custom audio device string for linux
        linux_audio_device = f'sysdefault:CARD={self.config.config["custom_audio_device_card"]}'
        if self.config.config['custom_audio_device_dev'] != '':
            linux_audio_device += f',DEV={self.config.config["custom_audio_device_dev"]}'

        # Beginning of the ffmpeg command for windows TODO: Add framerate
        windows_command_template = ['ffmpeg','-hide_banner','-y','-f','dshow','-vcodec',input_format,'-framerate',framerate,'-video_size',input_resolution,'-i',f'video={video_device}:audio={audio_device}']
        # Beginning of the ffmpeg command for linux
        linux_command_template = ['ffmpeg','-hide_banner','-y','-f','v4l2','-input_format',input_format,'-framerate',framerate,'-err_detect','ignore_err','-video_size',input_resolution,'-i',f'{video_device}','-f','alsa','-i',linux_audio_device]
        
        # Select the correct command template based on the OS
        if os.name == 'nt':
            ffmpeg_command = windows_command_template
        elif os.name == 'posix':
            ffmpeg_command = linux_command_template
        else:
            raise Exception('OS not supported')
        
        # Add stream copy if necessary
        if self.config.config[video_device_config]['streamcopy']:
            ffmpeg_command.extend(['-codec:v', 'copy', '-codec:a', 'copy'])
        
        ffmpeg_command.append(recording_file) # Add the output file

        # Run the ffmpeg command
        self.recording_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

    def stop_recording(self):
        # Tell ffmpeg to stop recording, and wait a bit for it to finish before terminating it
        self.recording_process.communicate(str.encode('q'))
        time.sleep(int(self.config.config['end_recording_delay']))
        self.recording_process.terminate()

        # Extract the audio from the video
        subprocess.run(['ffmpeg','-hide_banner','-y','-i',TEMP_VIDEO_FILES[self.video_device_index],'-codec:a','libmp3lame',TEMP_AUDIO_FILE])

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
        video_fps = video.get(cv2.CAP_PROP_FPS)
        video_framecount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_file = cv2.VideoWriter(TEMP_PROCESSED_VIDEO_FILE, fourcc, video_fps, (1920, 1080))

        # Testing purposes
        processing_start_time = time.time()

        self.transform_matrix = self.get_warp_matrix(video_device_index)

        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break # Break if there is no more video

            # Replace the frame with the birds eye view
            output = self.birds_eye_view(frame, video_device_index)
            output = cv2.resize(output, (1920, 1080), interpolation=cv2.INTER_AREA) # apparently necessary on linux???
            out_file.write(output)

        video.release()
        out_file.release()

        # Testing purposes
        processing_finish_time = time.time()
        print(f"Processed {video_framecount} frames in {processing_finish_time - processing_start_time} seconds")

    def combine_video_and_audio(self):
        output_filename = self.config.config['output_video_file']
        # Use ffmpeg to combine the new silent video with the audio from the original video
        subprocess.run(['ffmpeg','-hide_banner','-i', TEMP_AUDIO_FILE, '-i',
                        TEMP_PROCESSED_VIDEO_FILE, '-y','-err_detect','ignore_err','-codec:a', 'copy', '-codec:v',
                        'copy', output_filename])
        print('Video saved to ' + output_filename)

    def get_warp_matrix(self, video_device=0):
        # Corners should be in this order
        # 0 1
        # 2 3

        # The problem right now is that the corners are rich from the aruco
        # but only points from the manual selection
        video_device_config = self.config.config['video'+str(video_device)]
        corners = video_device_config['corners']
        # Make a copy of the corners
        corners = corners.copy()
        corners[2], corners[3] = corners[3], corners[2]

        init_corners = np.array(corners, dtype="float32")  # initial corners from the arguments
        dest_corners = np.array([[0, 0], [1000, 0], [1000, 1000], [0, 1000]],
                                dtype="float32")  # destination corners in a square

        # Compute the perspective transform matrix and then apply it
        transform_matrix = cv2.getPerspectiveTransform(init_corners, dest_corners)
        return transform_matrix

    def birds_eye_view(self, img, video_device=0):
        # start_time = time.time()
        video_device_config = self.config.config['video'+str(video_device)]
        
        warped = cv2.warpPerspective(img, self.transform_matrix, (1000, 1000))

        # Debug:
        # for corner in corners:
        #     img = cv2.circle(img, corner, 10, (0, 0, 255), -1)
        resized = cv2.resize(warped, video_device_config['resolution'], interpolation=cv2.INTER_AREA)

        # finish_time = time.time()
        # print(f"Time to process frame: {finish_time - start_time}")

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
                # print(frame.shape) # Debug to see the resolution
                return frame
            
    def warp_frame(self):
        # Debug
        # warped_frame = self.frame
        # for corner in self.config.config['video'+str(video_device)]['corners']:
        #     warped_frame = cv2.circle(self.frame, corner, 10, (0, 0, 255), -1)
        self.processing.transform_matrix = self.processing.get_warp_matrix()
        return self.processing.birds_eye_view(self.frame)