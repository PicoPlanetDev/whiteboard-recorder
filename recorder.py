import time
import subprocess
import yaml
import cv2
import numpy as np
import os

class Configuration():
    def __init__(self):
        self.get_av_splits()

        self.load_config()

        if not self.get_value('is_configured'):
            self.configure()

    def get_av_splits(self):
        # import shlex
        # shlex.split("ffmpeg -list_devices true -f dshow -i dummy")
        # Immediate exit requested, so stderr is used
        output = subprocess.run(
            ['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy'],
            capture_output=True).stderr.decode('utf-8')

        self.av_splits = output.split('(video)')

    def get_video_devices(self):
        video_section = self.av_splits[:len(self.av_splits) - 1]

        # Since we split by (video), each video device is in a separate item
        self.video_devices = []
        for item in video_section:
            self.video_devices.append(item.split('"')[-2])

        return self.video_devices

    def get_audio_devices(self):
        audio_section = self.av_splits[len(self.av_splits) - 1:]

        # len(audio_section) returns 1 so we just split by quotes
        audio_section_items = audio_section[0].split('"')
        # 3 7 11 seems to be counting by 4 starting at 3
        self.audio_devices = audio_section_items[3::4]

        return self.audio_devices

    def load_config(self):
        try:
            with open('config.yaml', 'r') as file:
                self.config = yaml.safe_load(file)
                return self.config
        except FileNotFoundError:
            self.create_default_config()
            return self.load_config()

    def create_default_config(self):
        default_video_device = self.get_video_devices()[0]
        default_audio_device = self.get_audio_devices()[0]
        default_config = {
            'video': default_video_device,
            'audio': default_audio_device,
            'is_configured': False,
            'input_resolution': '1920x1080',
            'top_left': [0, 0],
            'top_right': [0, 0],
            'bottom_right': [0, 0],
            'bottom_left': [0, 0],
            'temp_video_file': 'temp_recording.mp4',
            'temp_processed_video_file': 'temp_processed_recording.mp4',
            'output_video_file': 'final_recording.mp4',
            'temp_audio_file': 'temp_audio.mp3',
        }
        with open('config.yaml', 'w') as file:
            yaml.dump(default_config, file)
        self.config = default_config
    
    def save_config(self):
        with open('config.yaml', 'w') as file:
            yaml.dump(self.config, file)

    def configure(self):
        def prompt_user_options_string(options, prompt='Select an option: '):
            """Prompts the user to select an option from a list of options.

            Args:
                options (list): List of string options to choose from.
                prompt (str, optional): The prompt text to show. Defaults to 'Select an option: '.

            Returns:
                str: The selected option.
            """
            for i, option in enumerate(options):
                print(f'{i}: {option}')
            try:
                return options[int(input(prompt))]
            except:
                print('Invalid selection')
                return prompt_user_options_string(options)

        def prompt_user_input_string(prompt, default):
            """Prompts the user to input a string.

            Args:
                prompt (str): The prompt text to show.
                default (str): If the user doesn't input anything, this is returned.

            Returns:
                str: The user's input, or the default if the user didn't input anything.
            """            
            user_input = input(prompt)
            if user_input == '': return default
            return user_input

        print("Whiteboard Recorder Configuration")

        # Configure the audio and video devices
        video_devices = self.get_video_devices()
        audio_devices = self.get_audio_devices()
        selected_video_device = prompt_user_options_string(video_devices, 'Select a video device: ')
        selected_audio_device = prompt_user_options_string(audio_devices, 'Select an audio device: ')
        self.set_value('video', selected_video_device)
        self.set_value('audio', selected_audio_device)

        # Configure the input resolution, default is 1920x1080
        input_resolution = prompt_user_input_string('Input resolution (1920x1080): ', '1920x1080')
        self.set_value('input_resolution', input_resolution)

        # Flag that the user has configured the program (so it doesn't prompt again)
        self.set_value('is_configured', True)

    def set_value(self, key, value):
        """Sets a value in the config.

        Args:
            key (str): The key to set the value of.
            value (any): The value to set.
        """        
        self.config[key] = value
        self.save_config()
    
    def get_value(self, key):
        """Gets a value from the config.

        Args:
            key (str): The key to get the value of.

        Returns:
            any: The value of the key.
        """
        return self.config[key]

class VideoRecorder():
    def __init__(self, config):
        self.config = config

    def start_recording(self):
        video_device = self.config.get_value('video')
        audio_device = self.config.get_value('audio')
        input_resolution = self.config.get_value('input_resolution')
        self.recording_process = subprocess.Popen(['ffmpeg', '-y', '-f', 'dshow', '-i', f'video={video_device}:audio={audio_device}', '-s', input_resolution, self.config.get_value('temp_video_file')], stdin=subprocess.PIPE)
        
    def stop_recording(self):
        # Tell ffmpeg to stop recording
        self.recording_process.communicate(str.encode('q'))
        time.sleep(1)
        self.recording_process.terminate()

        # Convert the video to mp3
        subprocess.run(['ffmpeg', '-i', self.config.get_value('temp_video_file'), '-y', '-codec:a', 'libmp3lame', self.config.get_value('temp_audio_file')])

    def clear_files(self):
        os.remove(self.config.get_value('temp_video_file'))
        os.remove(self.config.get_value('temp_audio_file'))
        os.remove(self.config.get_value('temp_processed_video_file'))
        os.remove(self.config.get_value('output_video_file'))

class Processing():
    def __init__(self, config):
        self.config = config
        
        self.get_corners()
        self.process_recording()
        self.combine_video_and_audio()
    
    def process_recording(self):
        video = cv2.VideoCapture(self.config.get_value('temp_video_file'))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_file = cv2.VideoWriter(self.config.get_value('temp_processed_video_file'), fourcc, 30.0, (1920, 1080))
        
        while video.isOpened():
            ret, frame = video.read()

            if not ret: break

            output = self.birds_eye_view(frame)
            out_file.write(output)
        
        video.release()
        out_file.release()

    def combine_video_and_audio(self):
        subprocess.run(['ffmpeg', '-i', self.config.get_value('temp_audio_file'), '-i', self.config.get_value('temp_processed_video_file'), '-y', '-codec:a', 'copy', '-codec:v', 'copy', self.config.get_value('output_video_file')])
        print(f'Video saved to {self.config.get_value("output_video_file")}')

    def get_corners_aruco(self):
        def get_markers(frame):
            """Detects ArUco markers in the frame and returns the corners of the markers

            Args:
                frame (np.array): Frame to detect markers in

            Raises:
                ValueError: Wrong number of markers detected (inluding no markers)
                ValueError: Could not read video file

            Returns:
                list: Corners of the markers
            """
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert to grayscale

            # detect markers
            arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
            arucoParam = cv2.aruco.DetectorParameters_create()
            bounding_boxes, ids, rejected = cv2.aruco.detectMarkers(gray, arucoDict, parameters = arucoParam)
            # cv2.aruco.drawDetectedMarkers(img, bounding_boxes, ids) # debugging

            # verify that four  markers were detected
            if len(bounding_boxes) != 4:
                raise ValueError(f"Wrong number of markers detected {len(bounding_boxes)}/4 expected")

            ids = ids.flatten() # flatten ids list
            
            markers = [] # create a blank list of marker corners to be populated

            # loop over the detected ArUCo corners
            # The sort is so corners indexes are in the same order as the ids
            for (marker_corners, marker_ids) in sorted(zip(bounding_boxes, ids), key=lambda x: x[1]):
                # corner order
                # 0 1
                # 3 2

                corners = marker_corners.reshape((4, 2)) # reshape the boxes into an array of 4 (x, y) coordinates
                (topLeft, topRight, bottomRight, bottomLeft) = corners

                # convert each of the (x, y)-coordinate pairs to integers
                topRight = (int(topRight[0]), int(topRight[1]))
                bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                topLeft = (int(topLeft[0]), int(topLeft[1]))

                markers.append([topLeft, topRight, bottomRight, bottomLeft])
            return markers

        cap = cv2.VideoCapture(self.config.get_value('temp_video_file'))
        num_undetected_frames = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: raise ValueError("Could not read video file")
            try:
                markers = get_markers(frame)
                cap.release()
                return markers
            except:
                num_undetected_frames += 1
                print(f'Could not detect ArUco markers in {num_undetected_frames}/10 frames')
                if num_undetected_frames >= 10:
                    cap.release()
                    raise Exception("Could not detect markers")

    def get_corners_manual(self):
        # get the first frame
        cap = cv2.VideoCapture(self.config.get_value('temp_video_file'))
        ret, frame = cap.read()
        cap.release()
        if not ret: raise ValueError("Could not read video file")

        scale_factor = 0.5
        frame = cv2.resize(frame, (int(frame.shape[1] * scale_factor), int(frame.shape[0] * scale_factor)))

        corners = []

        def mouse_callback(event, x, y, flags, params):
            if event == cv2.EVENT_LBUTTONDOWN:
                if len(corners) < 4:
                    x_scaled, y_scaled = int(x / scale_factor), int(y / scale_factor)
                    corners.append([x_scaled,y_scaled])
                    print(f'Added corner {x},{y}')
                    cv2.circle(frame, (x,y), 5, (255,0,0), -1)
                    cv2.imshow('Select corners', frame)
                
                if len(corners) >= 4:
                    cv2.putText(frame, 'Press any key to continue', (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.imshow('Select corners', frame)

        cv2.namedWindow('Select corners')
        cv2.setMouseCallback('Select corners', mouse_callback)

        frame = cv2.putText(frame, 'Click corners clockwise from top left', (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)

        cv2.imshow('Select corners', frame)
        cv2.waitKey(0)
        return corners
                    
    def birds_eye_view(self, img):
        # Corners should be in this order
        # 0 1
        # 2 3

        # The problem right now is that the corners are rich from the aruco
        # but only points from the manual selection        

        init_corners = np.array(self.corners, dtype="float32") # initial corners from the arguments
        dest_corners = np.array([[0, 0], [800, 0], [800, 800], [0, 800]], dtype="float32") # destination corners in a square
        
        # Compute the perspective transform matrix and then apply it
        transform_matrix = cv2.getPerspectiveTransform(init_corners, dest_corners)
        warped = cv2.warpPerspective(img, transform_matrix, (800, 800))
        resized = cv2.resize(warped, (1920, 1080))

        return resized

    def get_corners(self):
        try:
            aruco_corners = self.get_corners_aruco()
            self.corners = [aruco_corners[0][0], aruco_corners[1][1], aruco_corners[3][2], aruco_corners[2][3]]
        except:
            corner_tests = ['top_left', 'top_right', 'bottom_right', 'bottom_left']
            for corner in corner_tests:
                if self.config.get_value(corner) == [0, 0]:
                    self.corners = self.get_corners_manual()
                    break
            else:
                self.corners = [self.config.get_value('top_left'), self.config.get_value('top_right'), self.config.get_value('bottom_right'), self.config.get_value('bottom_left')]

        # Save the corners for later in the config file
        top_left, top_right, bottom_right, bottom_left = self.corners
        self.config.set_value('top_left', top_left)
        self.config.set_value('top_right', top_right)
        self.config.set_value('bottom_right', bottom_right)
        self.config.set_value('bottom_left', bottom_left)

if __name__ == '__main__':
    print("Whiteboard Recorder")
    print("If you'd like to change the configuration, change the is_configured value to False in config.yaml and restart the program")
    config = Configuration()
    recorder = VideoRecorder(config)
    recorder.start_recording()
    time.sleep(5)
    recorder.stop_recording()
    processing = Processing(config)