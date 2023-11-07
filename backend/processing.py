import cv2
import numpy as np
import time
import subprocess
import os

class Processing():
    def __init__(self, config):
        self.config = config

    def process_recording(self, video_device_index=0):
        # Get the file paths
        temp_video_file = self.config.config['files']['temp_video_files'][video_device_index]
        temp_processed_video_file = self.config.config['files']['temp_processed_video_file']

        # Create the video capture and get its properties
        video = cv2.VideoCapture(temp_video_file)
        video_fps = video.get(cv2.CAP_PROP_FPS)
        video_framecount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        # Create the video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_file = cv2.VideoWriter(temp_processed_video_file, fourcc, video_fps, (1920, 1080))

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
    
def convert_to_jpeg(frame: np.ndarray):
    """Converts an OpenCV image to a jpeg

    Args:
        frame (np.ndarray): The OpenCV image

    Returns:
        bytes: The jpeg encoded bytes of the image
    """    
    ret, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()