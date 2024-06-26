import toml
import os
import subprocess
import pathlib

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
            # TODO: for device in /dev/video* get the name I guess is an option
            self.audio_devices = [[0, 'default']] # Not an actual thing
        else:
            raise Exception('OS not supported')

        self.config = self.load_config()
        

    def get_video_devices(self) -> list[tuple[str, str]]:
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

    def get_audio_devices(self) -> list[tuple[str, str]]:
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

    def load_config(self) -> dict:
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
            'stack': 'vstack', # 'vstack' or 'hstack'
            'job_name_format': '%m-%d-%Y %H-%M-%S',
            'stack_order': [0, 1],
            'auto_process_recordings': True,
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
                'temp_video_file': 'temp_video0.mkv',
                'temp_processed_video_file': 'temp_processed_video0.mp4',
                'pixel_format': '',
                'focus': -1,
                'autodetect_corners': False,
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
                'temp_video_file': 'temp_video1.mkv',
                'temp_processed_video_file': 'temp_processed_video1.mp4',
                'pixel_format': '',
                'focus': -1,
                'autodetect_corners': False,
            },
            'files': {
                'temp_audio_file': 'temp_audio.mp3',
                'output_video_file': 'output_video.mp4',
                'stacked_video_file': 'stacked_video.mp4',
                'recording_directory': pathlib.Path('./recordings').as_posix(),
                'recording_copy_directory': '',
            },
            'periods': {
                'enabled': False,
                'names': '',
                'times': ''
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
            'custom_audio_device_card': self.config['custom_audio_device_card'],
            'custom_audio_device_dev': self.config['custom_audio_device_dev'],
            'end_recording_delay': self.config['end_recording_delay'],
            'stack': self.config['stack'],
            'job_name_format': self.config['job_name_format'],
            'stack_order': self.config['stack_order'],
            'auto_process_recordings': self.config['auto_process_recordings'],
            'video0': {
                'video_device': self.config['video0']['video_device'],
                'resolution': self.config['video0']['resolution'],
                'enabled': self.config['video0']['enabled'],
                'custom_video_device': self.config['video0']['custom_video_device'],
                'custom_video_device_index': self.config['video0']['custom_video_device_index'],
                'streamcopy': self.config['video0']['streamcopy'],
                'framerate': self.config['video0']['framerate'],
                'input_format': self.config['video0']['input_format'],
                'temp_video_file': self.config['video0']['temp_video_file'],
                'temp_processed_video_file': self.config['video0']['temp_processed_video_file'],
                'pixel_format': self.config['video0']['pixel_format'],
                'focus': self.config['video0']['focus'],
                'autodetect_corners': self.config['video0']['autodetect_corners'],
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
                'temp_video_file': self.config['video1']['temp_video_file'],
                'temp_processed_video_file': self.config['video1']['temp_processed_video_file'],
                'pixel_format': self.config['video1']['pixel_format'],
                'focus': self.config['video1']['focus'],
                'autodetect_corners': self.config['video1']['autodetect_corners'],
            },
            'files': {
                'temp_audio_file': self.config['files']['temp_audio_file'],
                'output_video_file': self.config['files']['output_video_file'],
                'stacked_video_file': self.config['files']['stacked_video_file'],
                'recording_directory': pathlib.Path(self.config['files']['recording_directory']).as_posix(),
                'recording_copy_directory': self.config['files']['recording_copy_directory'],
            },
            'periods': {
                'enabled': self.config['periods']['enabled'],
                'names': self.config['periods']['names'],
                'times': self.config['periods']['times']
            }
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

        # Validate stack
        if not isinstance(data['stack'], str):
            raise TypeError("Expected stack to be a string")
        if data['stack'] not in ['vstack', 'hstack']:
            raise ValueError("Expected stack to be 'vstack' or 'hstack'")
        self.config['stack'] = data['stack']

        # Validate job_name_format
        if not isinstance(data['job_name_format'], str):
            raise TypeError("Expected job_name_format to be a string")
        if data['job_name_format'] == '':
            raise ValueError("Expected job_name_format to not be empty")
        for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
            if char in data['job_name_format']:
                raise ValueError(f"Expected job_name_format to not contain {char}")
        self.config['job_name_format'] = data['job_name_format']

        # Validate stack_order
        if not isinstance(data['stack_order'], list):
            raise TypeError("Expected stack_order to be a list")
        if len(data['stack_order']) != 2:
            raise ValueError("Expected stack_order to be a list of length 2")
        for i in data['stack_order']:
            if not isinstance(i, int):
                raise TypeError("Expected stack_order to be a list of ints")
        self.config['stack_order'] = data['stack_order']

        # Validate auto process recordings
        if not isinstance(data['auto_process_recordings'], bool):
            raise TypeError("Expected auto_process_recordings to be a bool")
        self.config['auto_process_recordings'] = data['auto_process_recordings']

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

            # Validate pixel_format
            if not isinstance(data[video]['pixel_format'], str):
                raise TypeError(f"Expected {video}['pixel_format'] to be a string")
            self.config[video]['pixel_format'] = data[video]['pixel_format']

            # Convert focus to int
            try:
                self.config[video]['focus'] = int(data[video]['focus'])
            except ValueError as e:
                raise TypeError(f"Expected {video}['focus'] to convert to an int ({e})")

            # Validate autodetect_corners
            if not isinstance(data[video]['autodetect_corners'], bool):
                raise TypeError(f"Expected {video}['autodetect_corners'] to be a bool")
            self.config[video]['autodetect_corners'] = data[video]['autodetect_corners']

        # Validate recording_directory
        if not isinstance(data['files']['recording_directory'], str):
            raise TypeError(f"Expected files['recording_directory'] to be a string")
        if data['files']['recording_directory'] == '':
            raise ValueError(f"Expected files['recording_directory'] to not be empty")
        self.config['files']['recording_directory'] = pathlib.Path(data['files']['recording_directory']).as_posix()

        # Validate recording_copy_directory
        if not isinstance(data['files']['recording_copy_directory'], str):
            raise TypeError(f"Expected files['recording_copy_directory'] to be a string")
        self.config['files']['recording_copy_directory'] = data['files']['recording_copy_directory']

        if not isinstance(data['periods']['enabled'], bool):
            raise TypeError(f"Expected periods['enabled'] to be a boolean")
        self.config['periods']['enabled'] = data['periods']['enabled']

        # Validate period names
        if not isinstance(data['periods']['names'], str):
            raise TypeError(f"Expected periods['names'] to be a comma-separated string")
        self.config['periods']['names'] = str(data['periods']['names']).strip()

        # Validate period times
        if not isinstance(data['periods']['times'], str):
            raise TypeError(f"Expected periods['times'] to be a comma-separated string")
        self.config['periods']['times'] = str(data['periods']['times']).strip()

        self.save_config()

    def get_video_device_index(self, video_device: str) -> int:
        if self.config[video_device]["custom_video_device_index"] != -1:
            return self.config[video_device]["custom_video_device_index"]
        else:
            return int(self.config[video_device]["video_device"][0])
        
    def get_video_device_name(self, video_device: str) -> str:
        if self.config[video_device]["custom_video_device"] != "":
            return self.config[video_device]["custom_video_device"]
        else:
            return self.config[video_device]["video_device"][1]

    def get_enabled_video_devices(self) -> list[str]:
            """
            Returns a list of enabled video devices based on the configuration.
            """
            enabled_video_devices = []
            for video_device in ['video0', 'video1']:
                if self.config[video_device]['enabled']:
                    enabled_video_devices.append(video_device)
            return enabled_video_devices
