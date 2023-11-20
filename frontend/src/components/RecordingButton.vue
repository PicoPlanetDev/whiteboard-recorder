<template>
    <button type="button" class="btn btn-success btn-lg px-3 me-2 my-2" @click="toggleRecording()"
        v-if="recording_status === false">
        <i class="bi bi-play-circle-fill"></i>
        Start recording
    </button>
    <button type="button" class="btn btn-danger btn-lg px-3 me-2 my-2" @click="toggleRecording()"
        v-if="recording_status === true">
        <i class="bi bi-stop-circle-fill"></i>
        Stop recording
    </button>
    <button type="button" class="btn btn-warning btn-lg px-3 me-2 my-2" v-if="recording_status === 'processing'">
        <div class="spinner-border spinner-border-sm" role="status"></div>
        Processing
    </button>
</template>

<script>
import axios from 'axios';

export default {
    name: 'RecordingButton',
    data() {
        return {
            recording_status: false,
            show_error: false,
        }
    },
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
        toggleRecording() {
            var newRecordingStatus = !this.recording_status;
            // if (!newRecordingStatus) {
            //     this.recording_status = 'processing';
            // }
            return axios.post('/toggle_recording', { recording_status: newRecordingStatus })
                .then(response => {
                    this.recording_status = response.data.recording_status;

                    if (response.data.status === 'error') {
                        this.show_error = true;
                    } else {
                        this.show_error = false;
                    }
                })
                .catch(error => {
                    console.log(error);
                });
        },
    },
    mounted() {
        this.getRecordingStatus();
    },

}
</script>