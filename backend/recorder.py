import time
import subprocess
import os
import contextlib
import time

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
        recording_file = self.config.config['files']['temp_video_files'][self.video_device_index]
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
        subprocess.run(['ffmpeg','-hide_banner','-y','-i',self.config.config['files']['temp_video_files'][self.video_device_index],'-codec:a','libmp3lame',self.config.config['files']['temp_audio_file']])

    def clear_files(self):
        with contextlib.suppress(FileNotFoundError): # Ignore if the file doesn't exist (likely)
            os.remove(self.config.config['files']['temp_video_files'][self.video_device_index])
            os.remove(self.config.config['files']['temp_audio_file'])
            os.remove(self.config.config['files']['temp_processed_video_file'])
            os.remove(self.config.config['files']['output_video_file'])