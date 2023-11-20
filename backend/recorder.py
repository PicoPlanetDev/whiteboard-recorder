import pathlib
import time
import subprocess
import os
import contextlib
import time
import pathlib

class VideoRecorder():
    def __init__(self, config):
        self.config = config
        self.recording_processes = []

    def start_recording(self, recording_directory: pathlib.Path):
        # Clear any files in the recording directory
        self.clear_files(recording_directory)

        for video_device in self.config.get_enabled_video_devices():
            # Get the video device config string
            video_device_config = self.config.config[video_device]

            # Get the configuration values that will be reused
            video_device_name = self.config.get_video_device_name(video_device)
            audio_device = self.config.config['audio_device'][1] # specifically the audio device name
            input_resolution = f"{video_device_config['resolution'][0]}x{video_device_config['resolution'][1]}"
            framerate = video_device_config["framerate"]

            # Create the file path for the recording
            recording_file = recording_directory.joinpath(pathlib.Path(video_device_config['temp_video_file']))

            # Put together the custom audio device string for linux
            linux_audio_device = f'sysdefault:CARD={self.config.config["custom_audio_device_card"]}'
            if self.config.config['custom_audio_device_dev'] != '':
                linux_audio_device += f',DEV={self.config.config["custom_audio_device_dev"]}'

            # Beginning of the ffmpeg command for windows TODO: Add framerate
            windows_command_template = ['ffmpeg','-hide_banner','-y','-f','dshow','-framerate',str(framerate),'-video_size',str(input_resolution),'-i',f'video={video_device_name}:audio={audio_device}']
            # Beginning of the ffmpeg command for linux
            linux_command_template = ['ffmpeg','-hide_banner','-y','-f','v4l2','-framerate',str(framerate),'-err_detect','ignore_err','-video_size',str(input_resolution),'-i',str(video_device_name),'-f','alsa','-i',str(linux_audio_device)]
            
            # Select the correct command template based on the OS
            if os.name == 'nt':
                ffmpeg_command = windows_command_template

                # Add pixel format and input format if necessary
                if video_device_config['pixel_format'] != '':
                    ffmpeg_command.insert(5, '-pixel_format')
                    ffmpeg_command.insert(6, video_device_config['pixel_format'])
                if video_device_config['input_format'] != '':
                    ffmpeg_command.insert(5, '-vcodec')
                    ffmpeg_command.insert(6, video_device_config['input_format'])
            elif os.name == 'posix':
                ffmpeg_command = linux_command_template

                # Add pixel format and input format if necessary
                if video_device_config['pixel_format'] != '':
                    ffmpeg_command.insert(5, '-pixel_format')
                    ffmpeg_command.insert(6, video_device_config['pixel_format'])
                if video_device_config['input_format'] != '':
                    ffmpeg_command.insert(5, '-input_format')
                    ffmpeg_command.insert(6, video_device_config['input_format'])

                # Focus the camera
                self.focus_camera(video_device)
            else:
                raise Exception('OS not supported')
            
            # Add stream copy if necessary
            if video_device_config['streamcopy']:
                ffmpeg_command.extend(['-codec:v', 'copy', '-codec:a', 'copy'])
            
            ffmpeg_command.append(recording_file) # Add the output file

            # Run the ffmpeg command
            self.recording_processes.append(subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE))

    def stop_recording(self):
        # Tell ffmpeg to stop recording
        for process in self.recording_processes:
            try:
                process.communicate(str.encode('q'))
            except Exception as e:
                print(e)
                pass

        time.sleep(int(self.config.config['end_recording_delay'])) # Wait a bit to make sure ffmpeg has time to stop recording gracefully
        # Terminate the ffmpeg processes
        for process in self.recording_processes:
            try:
                process.terminate()
            except Exception as e:
                print(e)
                pass

    def clear_files(self, recording_directory: pathlib.Path):
        # TODO: Support new jobs system
        with contextlib.suppress(FileNotFoundError): # Ignore if the file doesn't exist
            # Video files
            for video_device in self.config.get_enabled_video_devices():
                os.remove(recording_directory.joinpath(self.config.config[video_device]['temp_video_file']).as_posix())
                os.remove(recording_directory.joinpath(self.config.config[video_device]['temp_processed_video_file']).as_posix())
            # General files
            os.remove(recording_directory.joinpath(self.config.config['files']['temp_audio_file']).as_posix())
            os.remove(recording_directory.joinpath(self.config.config['files']['output_video_file']).as_posix())

    def focus_camera(self, video_device):
        """Sets the focus of the camera to the value specified in the config file
        Only works on linux right now because of the v4l2-ctl command

        Args:
            video_device (str): The internal name of the video device to focus (either video0 or video1)
        """
        if os.name != 'posix':
            print('Focus not supported on this OS')
            return

        video_device_name = self.config.get_video_device_name(video_device)
        video_device_config = self.config.config[video_device]

        # Enable autofocus if necessary
        if int(video_device_config['focus']) == -1:
            subprocess.run(['v4l2-ctl', '-d', video_device_name, '-c', 'focus_automatic_continuous=1'])
        else:
            subprocess.run(['v4l2-ctl', '-d', video_device_name, '-c', 'focus_automatic_continuous=0'])
            subprocess.run(['v4l2-ctl', '-d', video_device_name, '-c', f'focus_absolute={video_device_config["focus"]}'])