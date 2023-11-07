import cv2
import numpy as np
import time
import subprocess
import os

class Processing():
    def __init__(self, config):
        self.config = config

    def process_recording(self):
        """Processes the video file that was just recorded"""
        for video_device in self.config.get_enabled_video_devices():
            print(f"Processing video from {video_device}")
            
            # Get the file paths
            temp_video_file = self.config.config[video_device]['temp_video_file']
            temp_processed_video_file = self.config.config[video_device]['temp_processed_video_file']

            self.process_video(temp_video_file, temp_processed_video_file, video_device)
        # Now we end up with two processed video files, one for each video device

    def process_video(self, input_file, output_file, video_device):
        # Create the video capture and get its properties
        video = cv2.VideoCapture(input_file)
        video_fps = video.get(cv2.CAP_PROP_FPS)
        video_framecount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        # Create the video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_file = cv2.VideoWriter(output_file, fourcc, video_fps, (1920, 1080))

        # Testing purposes
        processing_start_time = time.time()

        self.transform_matrix = self.get_warp_matrix(video_device)

        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break # Break if there is no more video

            # Replace the frame with the birds eye view
            output = self.birds_eye_view(frame, video_device)
            output = cv2.resize(output, (1920, 1080), interpolation=cv2.INTER_AREA) # apparently necessary on linux???
            out_file.write(output)

        video.release()
        out_file.release()

        # Testing purposes
        processing_finish_time = time.time()
        elapsed = processing_finish_time - processing_start_time
        print(f"Processed {video_framecount} frames in {elapsed} seconds: {video_framecount/elapsed} fps")

    def combine_video_and_audio(self):
        """Combines the processed video and the audio from the original video into one video file with sound"""
        # Get the file paths
        temp_audio_file = self.config.config['files']['temp_audio_file']
        temp_processed_video_file = self.config.config['files']['temp_processed_video_file']
        output_video_file = self.config.config['files']['output_video_file']

        # Use ffmpeg to combine the new silent video with the audio from the original video
        subprocess.run(['ffmpeg','-hide_banner','-y',
                        '-i', temp_audio_file, '-i',temp_processed_video_file,'-err_detect','ignore_err',
                        '-codec:a', 'copy', '-codec:v','copy',
                        output_video_file])
        
        print(f'Video saved to {output_video_file}')

    def stack_processed_videos(self):
        """Stacks the processed videos on top of each other"""
        print("Stacking processed videos")
        # Get the file paths
        temp_processed_video_files = [self.config.config[video_device]['temp_processed_video_file'] for video_device in self.config.get_enabled_video_devices()]
        # stacked_video_file = self.config.config['files']['stacked_video_file']
        temp_audio_file = self.config.config['files']['temp_audio_file']

        output_video_file = self.config.config['files']['output_video_file']

        # Use ffmpeg to stack the processed videos on top of each other
        subprocess.run(['ffmpeg','-hide_banner','-y',
                        '-i', temp_processed_video_files[0], '-i',temp_processed_video_files[1],
                        '-i', temp_audio_file,
                        '-err_detect','ignore_err',
                        '-filter_complex', self.config.config['stack'],
                        '-r', '30',
                        output_video_file])

    def get_warp_matrix(self, video_device='video0'):
        # Corners should be in this order
        # 0 1
        # 2 3

        corners = self.config.config[video_device]['corners']
        # Make a copy of the corners
        corners = corners.copy()
        corners[2], corners[3] = corners[3], corners[2]

        init_corners = np.array(corners, dtype="float32")  # initial corners from the arguments
        dest_corners = np.array([[0, 0], [1000, 0], [1000, 1000], [0, 1000]],
                                dtype="float32")  # destination corners in a square

        # Compute the perspective transform matrix and then apply it
        transform_matrix = cv2.getPerspectiveTransform(init_corners, dest_corners)
        return transform_matrix

    def birds_eye_view(self, img, video_device='video0'):
            """
            Applies a perspective transform to the input image to obtain a bird's eye view.
            
            Args:
                img (numpy.ndarray): The input image to transform.
                video_device (str): The name of the video device to use for configuration.
            
            Returns:
                numpy.ndarray: The transformed image with a bird's eye view.
            """
            warped = cv2.warpPerspective(img, self.transform_matrix, (1000, 1000))

            # Uncomment to draw the corners for debugging
            # for corner in corners:
            #     img = cv2.circle(img, corner, 10, (0, 0, 255), -1)

            resized = cv2.resize(warped, self.config.config[video_device]['resolution'], interpolation=cv2.INTER_AREA)

            return resized

class Preview():
    def __init__(self, config, processing):
        self.config = config
        self.frame = None
        self.processing = Processing(config)

    def capture_frame(self, video_device='video0'):
            """
            Captures a frame from the specified video device.

            Args:
                video_device (str): The name of the video device to capture from. Defaults to 'video0'.

            Returns:
                numpy.ndarray: The captured frame as a numpy array.
            """
            if os.name == 'nt':
                cap = cv2.VideoCapture(self.config.get_video_device_index(video_device), cv2.CAP_DSHOW) # windows is slow if you don't use dshow
            else:
                cap = cv2.VideoCapture(self.config.get_video_device_index(video_device))
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.config[video_device]['resolution'][0]) # set the X resolution
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.config[video_device]['resolution'][1]) # set the Y resolution

            while True:
                ret, frame = cap.read()
                if ret:
                    cap.release()
                    self.frame = frame
                    return frame
            
    def warp_frame(self, video_device='video0'):
        # Debug
        # warped_frame = self.frame
        # for corner in self.config.config['video'+str(video_device)]['corners']:
        #     warped_frame = cv2.circle(self.frame, corner, 10, (0, 0, 255), -1)
        self.processing.transform_matrix = self.processing.get_warp_matrix(video_device)
        return self.processing.birds_eye_view(self.frame)
    
def convert_to_jpeg(frame: np.ndarray):
    """Converts an OpenCV image to a jpeg

    Args:
        frame (np.ndarray): The OpenCV image

    Returns:
        bytes: The jpeg encoded bytes of the image
    """    
    ret, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()