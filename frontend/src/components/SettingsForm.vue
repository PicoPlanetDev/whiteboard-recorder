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
                        <option v-for="device in audioDevices" :key="device[0]" :value="device[0]">
                            {{ device[1] }}
                        </option>
                    </select>
                </div>
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-6 border rounded">
                <div class="row">
                    <div class="col fs-5">Video 0</div>
                    <div class="col">
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" role="switch" id="video0CheckSwitch"
                                v-model="video0.enabled">
                            <label class="form-check-label" for="video0CheckSwitch">Video 0 enabled</label>
                        </div>
                    </div>
                </div>

                <!-- Video 0 -->
                <div class="row" v-if="video0.enabled">
                    <div class="mb-3">
                        Video device
                        <select class="form-select" v-model="video0.videoDevice">
                            <option disabled value="">Please select one</option>
                            <option v-for="device in videoDevices" :key="device[0]" :value="device[0]">
                                {{ device[1] }}
                            </option>
                        </select>
                    </div>

                    <div class="mb-3">
                        <label for="resolution-x" class="form-label">Video resolution</label>
                        <div class="input-group">
                            <input type="number" class="form-control" id="resolution-x" placeholder="1920"
                                v-model="video0.resolutionX">
                            <span class="input-group-text">x</span>
                            <input type="number" class="form-control" id="resolution-y" placeholder="1080"
                                v-model="video0.resolutionY">
                        </div>
                    </div>
                </div>
            </div>
            <!-- Video 1 -->
            <div class="col-6 border rounded bg-danger-subtle">
                <div class="row">
                    <div class="col fs-5">Video 1</div>
                    <div class="col">NOT IMPLEMENTED</div>
                    <div class="col">
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" role="switch" id="video1CheckSwitch"
                                v-model="video1.enabled">
                            <label class="form-check-label" for="video1CheckSwitch">Video 1 enabled</label>
                        </div>
                    </div>
                </div>
                <div class="row" v-if="video1.enabled">
                    <div class="mb-3">
                        Video device
                        <select class="form-select" v-model="video1.videoDevice">
                            <option disabled value="">Please select one</option>
                            <option v-for="device in videoDevices" :key="device[0]" :value="device[0]">
                                {{ device[1] }}
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
            audioInputDevice: 0,

            video0: {
                videoDevice: 0,
                resolutionX: '',
                resolutionY: '',
                enabled: false,
            },

            video1: {
                videoDevice: 0,
                resolutionX: '',
                resolutionY: '',
                enabled: false,
            }
        }
    },
    methods: {
        resetForm() {
            axios.get('/settings')
                .then(response => {
                    this.audioDevices = response.data.audio_devices;
                    this.videoDevices = response.data.video_devices;

                    this.audioInputDevice = response.data.audio_input_device[0];

                    this.video0.videoDevice = response.data.video0.video_device[0];
                    this.video0.resolutionX = response.data.video0.resolution[0];
                    this.video0.resolutionY = response.data.video0.resolution[1];
                    this.video0.enabled = response.data.video0.enabled;

                    this.video1.videoDevice = response.data.video1.video_device[0];
                    this.video1.resolutionX = response.data.video1.resolution[0];
                    this.video1.resolutionY = response.data.video1.resolution[1];
                    this.video1.enabled = response.data.video1.enabled;
                })
                .catch(error => {
                    console.log(error);
                });
        },
        saveSettings() {
            axios.post('/settings', {
                audio_input_device: this.audioDevices[this.audioInputDevice],
                video0: {
                    video_device: this.videoDevices[this.video0.videoDevice],
                    resolution: [this.video0.resolutionX, this.video0.resolutionY],
                    enabled: this.video0.enabled,
                },
                video1: {
                    video_device: this.videoDevices[this.video1.videoDevice],
                    resolution: [this.video1.resolutionX, this.video1.resolutionY],
                    enabled: this.video1.enabled,
                },
            })
                .then(response => {
                    if (response.data.success) {
                        this.resetForm();
                    }
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