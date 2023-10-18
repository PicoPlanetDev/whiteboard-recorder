<script setup>
import RecordingButton from './RecordingButton.vue';
</script>

<template>
    <RecordingButton />
    <a class="btn btn-primary btn-lg px-4 me-2 my-2" :href="downloadUrl">
        <i class="bi bi-file-earmark-arrow-down-fill"></i>
        Download recording
    </a>
</template>

<script>
import axios from 'axios';

export default {
    name: 'ButtonGroup',
    methods: {
        downloadRecording() {
            console.log("download recording");
        }
    },
    computed: {
        downloadUrl() {
            return axios.defaults.baseURL + '/download_recording';
        }
    },
}
</script>