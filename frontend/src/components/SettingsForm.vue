<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script >

<template>
    <form>
        <div class="row border rounded mb-3">
            <div class="col">
                <div class="mb-3">
                    Audio input device
                    <select class="form-select" v-model="audioInputDevice">
                        <option disabled value="">Please select one</option>
                        <option v-for="device in audioDevices" :key="device.id" :value="device.id">
                            {{ device.name }}
                        </option>
                    </select>
                </div>
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-6 border rounded">
                <div class="fs-5 text-center">Video 1</div>

                <div class="mb-3">
                    Video device
                    <select class="form-select" v-model="video1.videoDevice">
                        <option disabled value="">Please select one</option>
                        <option v-for="device in videoDevices" :key="device.id" :value="device.id">
                            {{ device.name }}
                        </option>
                    </select>
                </div>

                <div class="mb-3">
                    <label for="resolution-x" class="form-label">Video resolution</label>
                    <div class="input-group">
                        <input type="number" class="form-control" id="resolution-x" placeholder="1920"
                            v-model="video1.resolutionX">
                        <span class="input-group-text">x</span>
                        <input type="number" class="form-control" id="resolution-y" placeholder="1080"
                            v-model="video1.resolutionY">
                    </div>
                </div>
            </div>
            <div class="col-6 border rounded bg-danger-subtle">
                <div class="fs-5 text-center">Video 2 (not functional)</div>

                <div class="mb-3">
                    Video device
                    <select class="form-select" v-model="video2.videoDevice">
                        <option disabled value="">Please select one</option>
                        <option v-for="device in videoDevices" :key="device.id" :value="device.id">
                            {{ device.name }}
                        </option>
                    </select>
                </div>

                <div class="mb-3">
                    <label for="resolution-x" class="form-label">Video resolution</label>
                    <div class="input-group">
                        <input type="number" class="form-control" id="resolution-x" placeholder="1920"
                            v-model="video2.resolutionX">
                        <span class="input-group-text">x</span>
                        <input type="number" class="form-control" id="resolution-y" placeholder="1080"
                            v-model="video2.resolutionY">
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col">
                <button type="reset" class="btn btn-outline-danger me-2" @click="resetForm()">
                    <i class="bi bi-trash"></i>
                    Discard
                </button>
                <button type="submit" class="btn btn-primary me-2" @click="saveSettings()">
                    <i class="bi bi-check2"></i>
                    Save
                </button>
            </div>
        </div>
    </form>
</template>

<script>
import axios from 'axios';

export default {
    name: 'SettingsForm',
    data() {
        return {
            audioDevices: [],
            videoDevices: [],
            audioInputDevice: '',

            video1: {
                videoDevice: '',
                resolutionX: '',
                resolutionY: '',
            },

            video2: {
                videoDevice: '',
                resolutionX: '',
                resolutionY: '',
            }
        }
    },
    methods: {
        resetForm() {
            axios.get('/settings')
                .then(response => {
                    this.audioDevices = response.data.audio_devices;
                    this.videoDevices = response.data.video_devices;

                    this.audioInputDevice = response.data.audio_input_device;
                    this.video1.videoDevice = response.data.video1.video_device;
                    this.video1.resolutionX = response.data.video1.resolution_x;
                    this.video1.resolutionY = response.data.video1.resolution_y;
                    this.video2.videoDevice = response.data.video2.video_device;
                    this.video2.resolutionX = response.data.video2.resolution_x;
                    this.video2.resolutionY = response.data.video2.resolution_y;
                })
                .catch(error => {
                    console.log(error);
                });
        },
        saveSettings() {
            axios.post('/settings', {
                    audio_input_device: this.audioInputDevice,
                    video1: {
                        video_device: this.video1.videoDevice,
                        resolution_x: this.video1.resolutionX,
                        resolution_y: this.video1.resolutionY,
                    },
                    video2: {
                        video_device: this.video2.videoDevice,
                        resolution_x: this.video2.resolutionX,
                        resolution_y: this.video2.resolutionY,
                    },
                })
                .then(response => {
                    console.log(response);
                })
                .catch(error => {
                    console.log(error);
                });
        },
    },
    mounted() {
        this.resetForm();
    },
}
</script>