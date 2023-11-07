import toml
import os
import subprocess

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
            'files': {
                'temp_video_files': ['temp_video0.mp4', 'temp_video1.mp4'],
                'temp_audio_file': 'temp_audio.mp3',
                'temp_processed_video_file': 'temp_processed_video.mp4',
                'output_video_file': 'output_video.mp4'
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
            'files': {
                'temp_video_files': self.config['files']['temp_video_files'],
                'temp_audio_file': self.config['files']['temp_audio_file'],
                'temp_processed_video_file': self.config['files']['temp_processed_video_file'],
                'output_video_file': self.config['files']['output_video_file']
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

        # Does not have anything for files yet

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
