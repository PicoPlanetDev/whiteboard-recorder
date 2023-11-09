<script setup>
import RecordingButton from './RecordingButton.vue';
</script>

<template>
    <RecordingButton />
    <a class="btn btn-primary btn-lg px-4 me-2 my-2" :href="downloadUrl">
        <i class="bi bi-file-earmark-arrow-down-fill"></i>
        Download recording
    </a>
    <button type="button" class="btn btn-primary btn-lg px-4 me-2 my-2" @click="processRecording">
        <i class="bi bi-gears"></i>
        Manually process recording
    </button>
</template>

<script>
import axios from 'axios';

export default {
    name: 'ButtonGroup',
    methods: {
        processRecording() {
            axios.get('/process_recording')
                .then(response => {
                    console.log(response);
                })
                .catch(error => {
                    console.log(error);
                });
        }
    },
    computed: {
        downloadUrl() {
            return axios.defaults.baseURL + '/download_recording';
        }
    },
}
</script>