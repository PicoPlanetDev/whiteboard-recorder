import time
import subprocess
import os
import contextlib
import time

class VideoRecorder():
    def __init__(self, config, video_device='video0'):
        self.config = config
        self.video_device = video_device
        self.recording_process = None

    def start_recording(self):
        # Get the video device config string
        video_device_config = self.config.config[video_device]

        # Get the configuration values that will be reused
        video_device = self.config.get_video_device_name(self.video_device)
        audio_device = self.config.config['audio_device'][1] # specifically the audio device name
        input_resolution = f"{video_device_config['resolution'][0]}x{video_device_config['resolution'][1]}"
        input_format = video_device_config['input_format']
        recording_file = video_device_config['temp_video_file']
        framerate = video_device_config["framerate"]

        # Put together the custom audio device string for linux
        linux_audio_device = f'sysdefault:CARD={self.config.config["custom_audio_device_card"]}'
        if self.config.config['custom_audio_device_dev'] != '':
            linux_audio_device += f',DEV={self.config.config["custom_audio_device_dev"]}'

        # Beginning of the ffmpeg command for windows TODO: Add framerate
        windows_command_template = ['ffmpeg','-hide_banner','-y','-f','dshow','-vcodec',str(input_format),'-framerate',str(framerate),'-video_size',str(input_resolution),'-i',f'video={video_device}:audio={audio_device}']
        # Beginning of the ffmpeg command for linux
        linux_command_template = ['ffmpeg','-hide_banner','-y','-f','v4l2','-input_format',str(input_format),'-framerate',str(framerate),'-err_detect','ignore_err','-video_size',str(input_resolution),'-i',str(video_device),'-f','alsa','-i',str(linux_audio_device)]
        
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
        subprocess.run(['ffmpeg','-hide_banner','-y','-i',self.config.config['files']['temp_video_files'][self.video_device_index],'-codec:a','libmp3lame',self.config.config['files']['temp_audio_file']])

    def clear_files(self):
        with contextlib.suppress(FileNotFoundError): # Ignore if the file doesn't exist
            os.remove(self.config.config[self.video_device]['temp_video_file'])
            os.remove(self.config.config['files']['temp_audio_file'])
            os.remove(self.config.config['files']['temp_processed_video_file'])
            os.remove(self.config.config['files']['output_video_file'])