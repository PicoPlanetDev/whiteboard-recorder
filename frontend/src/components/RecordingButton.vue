<template>
    <button type="button" class="btn btn-success btn-lg px-3 me-2 my-2" @click="toggleRecording"
        v-if="recording_status === false">
        <i class="bi bi-play-circle-fill"></i>
        Start recording
    </button>
    <button type="button" class="btn btn-danger btn-lg px-3 me-2 my-2" @click="toggleRecording"
        v-if="recording_status === true">
        <i class="bi bi-stop-circle-fill"></i>
        Stop recording
    </button>
</template>

<script>
import axios from 'axios';

export default {
    name: 'RecordingButton',
    methods: {
        getRecordingStatus() {
            return axios.get('/recording_status')
                .then(response => {
                    this.recording_status = response.data.recording_status;
                })
                .catch(error => {
                    console.log(error);
                });
        },
    },
    toggleRecording() {
        if (this.recording_status === false) {
            this.startRecording();
        } else {
            this.stopRecording();
        }
    },
    startRecording() {
        return axios.post('/start_recording')
            .then(response => {
                this.recording_status = response.data.recording_status;
            })
            .catch(error => {
                console.log(error);
            });
    },
    stopRecording() {
        return axios.post('/stop_recording')
            .then(response => {
                this.recording_status = response.data.recording_status;
            })
            .catch(error => {
                console.log(error);
            });
    },
}
</script>