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

        <!-- Modal launcher button -->
        <div class="row mb-3">
            <button type="button" class="btn btn-outline-secondary" data-bs-toggle="modal"
                data-bs-target="#videoConfigurator" @click="getCorners">
                Launch video configurator
            </button>
        </div>

        <!-- Discard and save buttons -->
        <div class="row mb-3">
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

    <!-- Modal itself -->
    <div class="modal fade" id="videoConfigurator" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1"
        aria-labelledby="videoConfiguratorLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg" ref="configuratorModal">
            <div class="modal-content">
                <div class="modal-header">
                    <h1 class="modal-title fs-5" id="videoConfiguratorLabel">Video Configurator</h1>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="row mb-2">
                        <div class="col">
                            <form>
                                <div>Edit video config:</div>
                                <div class="form-check form-check-inline">
                                    <input class="form-check-input" type="radio" name="inlineRadioOptions" id="video0Radio"
                                        value="0" checked v-model="configurator.currentVideoDevice"
                                        @change="resetConfigurator">
                                    <label class="form-check-label" for="video0Radio">Video 1</label>
                                </div>
                                <div class="form-check form-check-inline">
                                    <input class="form-check-input" type="radio" name="inlineRadioOptions" id="video1Radio"
                                        value="1" v-model="configurator.currentVideoDevice" @change="resetConfigurator">
                                    <label class="form-check-label" for="video1Radio">Video 2</label>
                                </div>
                            </form>
                        </div>
                        <div class="col"><button type="reset" class="btn btn-primary me-2" @click="captureFrame">
                                <i class="bi bi-camera"></i>
                                Capture frame
                            </button>
                        </div>
                    </div>
                    <div class="row mb-2">
                        <div class="col">
                            <!-- <div><img :src="configurator.capturedFrame" class="img-fluid rounded"></div> -->
                            <div id="pointerDiv" class=""
                                :style="'background-image: url(' + configurator.capturedFrame + '); width: 100%; aspect-ratio: ' + getVideoAspectRatio(configurator.currentVideoDevice) + '; background-size: contain;'"
                                @click="imageClicked">
                                <i id="pointerDot" class="bi bi-plus text-primary"
                                    :style="'left: ' + configurator.crosshairPositions[0][0] + 'px; top: ' + configurator.crosshairPositions[0][1] + 'px; visibility: ' + configurator.crosshairVisibility[0] + ';'"></i>
                                <i id="pointerDot" class="bi bi-plus text-success"
                                    :style="'left: ' + configurator.crosshairPositions[1][0] + 'px; top: ' + configurator.crosshairPositions[1][1] + 'px; visibility: ' + configurator.crosshairVisibility[1] + ';'"></i>
                                <i id="pointerDot" class="bi bi-plus text-warning"
                                    :style="'left: ' + configurator.crosshairPositions[2][0] + 'px; top: ' + configurator.crosshairPositions[2][1] + 'px; visibility: ' + configurator.crosshairVisibility[2] + ';'"></i>
                                <i id="pointerDot" class="bi bi-plus text-danger"
                                    :style="'left: ' + configurator.crosshairPositions[3][0] + 'px; top: ' + configurator.crosshairPositions[3][1] + 'px; visibility: ' + configurator.crosshairVisibility[3] + ';'"></i>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="row mb-2">
                            <div class="col">
                                <label for="corner-tl-x" class="form-label">Top left</label>

                                <!-- Select corner buttons -->
                                <input type="radio" class="btn-check" id="radio-tl" name="pointer-radio" autocomplete="off"
                                    value="0" v-model="configurator.currentCorner" checked>
                                <label for="radio-tl" class="ms-2 btn btn-sm btn-outline-primary"><i
                                        class="bi bi-cursor-fill"></i></label>

                                <div class="input-group">
                                    <input type="number" class="form-control" id="corner-tl-x" placeholder="0"
                                        v-model="configurator.corners[0][0]">
                                    <span class="input-group-text">x</span>
                                    <input type="number" class="form-control" id="corner-tl-y" placeholder="0"
                                        v-model="configurator.corners[0][1]">
                                </div>
                            </div>
                            <div class="col">
                                <label for="corner-tr-x" class="form-label">Top right</label>

                                <!-- Select corner buttons -->
                                <input type="radio" class="btn-check" id="radio-tr" name="pointer-radio" autocomplete="off"
                                    value="1" v-model="configurator.currentCorner">
                                <label for="radio-tr" class="ms-2 btn btn-sm btn-outline-success"><i
                                        class="bi bi-cursor-fill"></i></label>

                                <div class="input-group">
                                    <input type="number" class="form-control" id="corner-tl-x" placeholder="0"
                                        v-model="configurator.corners[1][0]">
                                    <span class="input-group-text">x</span>
                                    <input type="number" class="form-control" id="corner-tl-y" placeholder="0"
                                        v-model="configurator.corners[1][1]">
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col">
                                <label for="corner-bl-x" class="form-label">Bottom left</label>

                                <!-- Select corner buttons -->
                                <input type="radio" class="btn-check" id="radio-bl" name="pointer-radio" autocomplete="off"
                                    value="2" v-model="configurator.currentCorner">
                                <label for="radio-bl" class="ms-2 btn btn-sm btn-outline-warning"><i
                                        class="bi bi-cursor-fill"></i></label>

                                <div class="input-group">
                                    <input type="number" class="form-control" id="corner-tl-x" placeholder="0"
                                        v-model="configurator.corners[2][0]">
                                    <span class="input-group-text">x</span>
                                    <input type="number" class="form-control" id="corner-tl-y" placeholder="0"
                                        v-model="configurator.corners[2][1]">
                                </div>
                            </div>
                            <div class="col">
                                <label for="corner-br-x" class="form-label">Bottom right</label>

                                <!-- Select corner buttons -->
                                <input type="radio" class="btn-check" id="radio-br" name="pointer-radio" autocomplete="off"
                                    value="3" v-model="configurator.currentCorner">
                                <label for="radio-br" class="ms-2 btn btn-sm btn-outline-danger"><i
                                        class="bi bi-cursor-fill"></i></label>

                                <div class="input-group">
                                    <input type="number" class="form-control" id="corner-tl-x" placeholder="0"
                                        v-model="configurator.corners[3][0]">
                                    <span class="input-group-text">x</span>
                                    <input type="number" class="form-control" id="corner-tl-y" placeholder="0"
                                        v-model="configurator.corners[3][1]">
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
                <div class="modal-footer">
                    <button type="reset" class="btn btn-outline-danger me-2" data-bs-dismiss="modal" @click="">
                        <i class="bi bi-trash"></i>
                        Discard
                    </button>
                    <button type="submit" class="btn btn-primary me-2" @click="saveCorners">
                        <i class="bi bi-check2"></i>
                        Save
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
#pointerDot {
    position: absolute;
    visibility: hidden;
    z-index: 2;
    font-size: 35px;
    pointer-events: none;
}
</style>

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
                corners: [[0, 0], [0, 0], [0, 0], [0, 0],],

            },
            video1: {
                videoDevice: 0,
                resolutionX: '',
                resolutionY: '',
                enabled: false,
                corners: [[0, 0], [0, 0], [0, 0], [0, 0],],
            },
            configurator: {
                capturedFrame: '',
                currentVideoDevice: 0,
                crosshairPositions: [[0, 0], [0, 0], [0, 0], [0, 0],],
                crosshairVisibility: ['hidden', 'hidden', 'hidden', 'hidden'],
                currentCorner: 0,
                corners: [[0, 0], [0, 0], [0, 0], [0, 0],],
            }
        }
    },
    computed: {

    },
    methods: {
        resetForm() {
            axios.get('/settings').then(response => {
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

            }).catch(error => {
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
                }

                ,
                video1: {
                    video_device: this.videoDevices[this.video1.videoDevice],
                    resolution: [this.video1.resolutionX, this.video1.resolutionY],
                    enabled: this.video1.enabled,
                }

                ,
            }).then(response => {
                if (response.data.success) {
                    this.resetForm();
                }

            }).catch(error => {
                console.log(error);
            });
        },
        captureFrame() {
            axios.post('/capture_frame', {

                video_device: this.configurator.currentVideoDevice,
            }).then(response => {
                this.configurator.capturedFrame = response.data;

            }).catch(error => {
                console.log(error);
            });
        },
        crosshairOffset([x, y]) {
            return [x - 3, y + 46];
        },
        // This is very hacky, and I can't even say it works
        imageClicked(event) {
            var currentCorner = parseInt(this.configurator.currentCorner);
            var modalOffsetX = this.$refs.configuratorModal.offsetLeft;
            var modalOffsetY = this.$refs.configuratorModal.offsetTop;
            var x = event.pageX - event.target.offsetLeft - modalOffsetX;
            var y = event.pageY - event.target.offsetTop - modalOffsetY - 64;
            this.configurator.crosshairPositions[currentCorner] = this.crosshairOffset([x, y]);
            this.configurator.crosshairVisibility[currentCorner] = 'visible';
            this.configurator.corners[currentCorner] = [x, y];

        },
        getVideoAspectRatio(video_device) {
            if (video_device == 0) {
                return this.video0.resolutionX / this.video0.resolutionY;
            } else if (video_device == 1) {
                return this.video1.resolutionX / this.video1.resolutionY;
            }
        },
        resetConfigurator(resetImage = false) {
            // Reset the captured frame if changing video device
            if (resetImage) {
                this.configurator.capturedFrame = '';
            }

            // Set new corner values based on current video device
            if (parseInt(this.configurator.currentVideoDevice) === 0) {
                this.configurator.corners = this.video0.corners;
            } else {
                this.configurator.corners = this.video1.corners;
            }

            this.configurator.currentCorner = 0;

            // Set crosshair positions using offset
            for (var i = 0; i < this.configurator.crosshairPositions.length; i++) {
                this.configurator.crosshairPositions[i] = this.crosshairOffset(this.configurator.corners[i]);
            }

            // Set crosshair visibility
            if (this.configurator.corners != [[0, 0], [0, 0], [0, 0], [0, 0],]) {
                this.configurator.crosshairVisibility = ['visible', 'visible', 'visible', 'visible'];
            } else {
                this.configurator.crosshairVisibility = ['hidden', 'hidden', 'hidden', 'hidden'];
            }
        },
        saveCorners() {
            axios.post('/corners', {

                video_device: this.configurator.currentVideoDevice,
                corners: this.configurator.corners,
            }).then(response => {
                if (response.data.success) {
                    this.getCorners();
                }

            }).catch(error => {
                console.log(error);
            });
        },
        getCorners() {
            axios.get('/corners').then(response => {
                this.video0.corners = response.data.video0;
                this.video1.corners = response.data.video1;
                this.resetConfigurator();

            }).catch(error => {
                console.log(error);
            });
        }
    },
    mounted() {
        this.resetForm();
    },
}

</script>
