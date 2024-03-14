import configuration
import recorder
import processing
import os
import time
import pathlib
import threading
import shutil
import datetime

class JobManager():
    def __init__(self, config: configuration.Configuration):
        self.config = config
        self.video_recorder = recorder.VideoRecorder(config)
        # self.processing_jobs = [ProcessingJob(config, 'test', pathlib.Path('recordings/test'))] # Test job
        self.processing_jobs = []
        self.current_recording_job_name = ''
        self.current_recording_job_directory = None # TODO: what's a default pathlib path

    def get_period_name(self):
        # current_time = time.time() # time since epoch

        period_names = str(self.config.config['periods']['names']).split(',') # ordered list of period names
        period_times = str(self.config.config['periods']['times']).split(',') # ordered list of period times

        period_times_split = [] # convert period_times to list of 2-item lists of hours and minutes
        for period_time in period_times:
            split_time = period_time.split(":") # split into hours and minutes
            period_times_split.append(int(split_time))
        
        # convert each period time to a time in seconds since epoch for today
        now = datetime.datetime.now()
        period_datetimes = [now.replace(hour=period_time_split[0], minute=period_time_split[1]) for period_time_split in period_times_split]

        # find the index of the period that the current time is in
        for i in range(len(period_datetimes)):
            if now >= period_datetimes[i]:
                return period_names[i]
        return None # if no period is found

    def start_recording(self):
        # Create a somehwat friendly job name based on the current time
        self.current_recording_job_name = time.strftime(self.config.config['job_name_format'], time.localtime())

        # Append the period name to the job name if periods are enabled
        if self.config.config['periods']['enabled']:
            period_name = self.get_period_name()
            if period_name:
                self.current_recording_job_name = f"{self.current_recording_job_name}_{period_name}"

        # Create a new directory for the job in the config's recording_directory, which might not already exist
        pathlib.Path(self.config.config['files']['recording_directory']).joinpath(pathlib.Path(self.current_recording_job_name)).mkdir(parents=True, exist_ok=True)
        self.current_recording_job_directory = pathlib.Path(self.config.config['files']['recording_directory']).joinpath(pathlib.Path(self.current_recording_job_name))

        self.video_recorder.start_recording(self.current_recording_job_directory)

    def stop_recording(self):
        self.video_recorder.stop_recording()
        self.processing_jobs.append(ProcessingJob(self.config, self.current_recording_job_name, self.current_recording_job_directory))

        # Automatically process the recording if auto_process_recordings is true
        if self.config.config['auto_process_recordings']:
            self.run_job(self.current_recording_job_name)

    def run_jobs(self):
        """Runs all the jobs in the processing_jobs list"""
        for job in self.processing_jobs:
            if not job.started:
                job.start()

    def run_job(self, job_name):
        """Runs the job with the given name
        
        Args:
            job_name (str): The name of the job to run
        """
        for job in self.processing_jobs:
            if job.job_name == job_name:
                if not job.started:
                    job.start()
                return
        raise Exception('Job not found')
    
    def get_job_status(self, job_name):
        """Returns the status of the job with the given name"""
        for job in self.processing_jobs:
            if job.job_name == job_name:
                return job.progress_message
        return 'Job not found'
    
    def get_all_jobs(self):
        """Returns a dictionary of the progress of all the jobs in the processing_jobs list"""
        jobs = []
        for job in self.processing_jobs:
            jobs.append({
                "name": job.job_name,
                "message": job.progress_message,
                "started": job.started,
                "finished": job.finished
            })
        return jobs
    
    def remove_job(self, job_name):
        """Removes the job with the given name from the processing_jobs list"""
        for job in self.processing_jobs:
            if job.job_name == job_name:
                if not job.started or job.finished:
                    self.processing_jobs.remove(job)
                return
        raise Exception('Job not found')
    
    def get_job_directory(self, job_name):
        """Returns the directory of the job with the given name"""
        for job in self.processing_jobs:
            if job.job_name == job_name:
                return job.recording_directory
        return 'Job not found'
    
    def get_job_output_file(self, job_name):
        """Returns the output file of the job with the given name"""
        for job in self.processing_jobs:
            if job.job_name == job_name:
                # output_file_name = self.config.config['files']['output_video_file']
                output_file_name = f"{job.job_name}.mp4"
                return job.recording_directory.joinpath(output_file_name)
        return 'Job not found'
    
    def clear_finished_jobs(self):
        """Removes all the finished jobs from the processing_jobs list"""
        for job in self.processing_jobs:
            if job.finished:
                self.processing_jobs.remove(job)

    def purge_recording_directory(self):
        """Removes all the files in the recording directory"""
        try:
            shutil.rmtree(self.config.config['files']['recording_directory'])
        except FileNotFoundError:
            print('Recording directory already non-existent')
            pass

class ProcessingJob():
    def __init__(self, config: configuration.Configuration, job_name: str, recording_directory: pathlib.Path):
        self.config = config
        self.video_processing = processing.Processing(config, recording_directory, job_name)
        self.job_name = job_name
        self.recording_directory = recording_directory
        self.started = False
        self.finished = False
        self.progress_message = 'Not started'

    def start(self):
        """Starts the processing job in a new thread"""
        self.started = True
        self.processing_thread = threading.Thread(target=self.process, daemon=True)
        self.processing_thread.start()
    
    def process(self):
        """Processes the recording"""
        self.progress_message = 'Extracting audio'
        self.video_processing.extract_audio()
        self.progress_message = 'Processing recording'
        self.video_processing.process_recording()
        self.progress_message = 'Stacking output'
        self.video_processing.stack_processed_videos()
        self.progress_message = 'Copying output'
        if self.config.config['files']['recording_copy_directory'] != '':
            if not pathlib.Path(self.config.config['files']['recording_copy_directory']).exists():
                pathlib.Path(self.config.config['files']['recording_copy_directory']).mkdir(parents=True, exist_ok=True)
            os.system(f'cp {self.recording_directory.joinpath(f"{self.job_name}.mp4").as_posix()} {pathlib.Path(self.config.config["files"]["recording_copy_directory"]).as_posix()}')
        self.progress_message = 'Finished'
        self.finished = True