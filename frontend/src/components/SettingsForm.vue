<script setup>
import Alert from './Alert.vue';
</script>

<template>
    <form>
        <!-- Alert -->
        <Alert :message="alert.message" :icon="alert.icon" :color="alert.color" v-if="alert.show"></Alert>
        <!-- Audio -->
        <div class="border rounded mb-3 p-3">
            <div class="mb-1">
                Audio input device
                <select class="form-select" v-model="audioInputDevice">
                    <option disabled value="">Please select one</option>
                    <option v-for="device in audioDevices" :key="device[0]" :value="device[0]">
                        {{ device[1] }}
                    </option>
                </select>
            </div>
            <div class="mb-3">
                Custom audio device (disabled if blank)
                <div class="input-group">
                    <span class="input-group-text">CARD</span>
                    <input type="text" class="form-control" placeholder="" aria-label="Custom audio device CARD"
                        v-model="customAudioDeviceCard">
                    <span class="input-group-text">DEV</span>
                    <input type="number" class="form-control" placeholder="" aria-label="Custom audio device DEV"
                        v-model="customAudioDeviceDev">
                </div>
            </div>
            <div class="mb-3">
                <label for="endRecordingDelayInput" class="form-label">End Recording Delay</label>
                <input type="number" id="endRecordingDelayInput" class="form-control"
                    aria-describedby="endRecordingDelayHelpBlock" v-model="endRecordingDelay">
                <div id="endRecordingDelayHelpBlock" class="form-text">
                    Delay in seconds before termination after the graceful stop signal is sent to the recording
                    process.
                </div>
            </div>
            <!-- Stack direction radio -->
            <div class="mb-3">
                Video stack direction
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="stackDirection" id="stackDirectionHorizontal"
                        value="hstack" v-model="stack">
                    <label class="form-check-label" for="stackDirectionHorizontal">Horizontal</label>
                </div>
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="stackDirection" id="stackDirectionVertical"
                        value="vstack" v-model="stack">
                    <label class="form-check-label" for="stackDirectionVertical">Vertical</label>
                </div>
            </div>
        </div>
        <!-- Video -->
        <div class="container-fluid">
            <div class="row mb-3">
                <!-- Video 0 -->
                <VideoSettings :videoNumber="0" :video="video0" :videoDevices="videoDevices"></VideoSettings>
                <!-- Video 1 -->
                <VideoSettings :videoNumber="1" :video="video1" :videoDevices="videoDevices"></VideoSettings>
            </div>

            <!-- Modal launcher button -->
            <div class="row mb-3">
                <button type="button" class="btn btn-outline-secondary" data-bs-toggle="modal"
                    data-bs-target="#videoConfigurator" @click="getCorners">
                    Launch video configurator
                </button>
            </div>
        </div>
        <div class="border rounded mb-3 p-3">
            <div class="fs-5 mb-3">Files</div>
            <!-- Job name format input -->
            <div class="mb-3">
                <label for="jobNameFormatInput" class="form-label">Job Name Format</label>
                <input type="text" id="jobNameFormatInput" class="form-control font-monospace"
                    aria-describedby="jobNameFormatHelpBlock" v-model="jobNameFormat">
                <div id="jobNameFormatHelpBlock" class="form-text">
                    <span class="font-monospace">time.strftime</span> string for naming jobs based on the current time.
                    See the <a href="https://docs.python.org/3/library/time.html#time.strftime" target="_blank">Python <span
                            class="font-monospace">time</span>
                        docs</a> for more information.
                </div>
            </div>
            <!-- Recording directory input -->
            <div class="mb-3">
                <label for="recordingDirectoryInput" class="form-label">Recording Directory</label>
                <input type="text" id="jrecordingDirectoryInput" class="form-control"
                    aria-describedby="recordingDirectoryHelpBlock" v-model="files.recordingDirectory">
                <div id="recordingDirectoryHelpBlock" class="form-text">
                    The path to a directory where recordings will be saved. If the directory does not exist, it will be
                    created when the first recording in the directory is started.
                </div>
            </div>
            <div>
                <button type="button" class="btn btn-danger me-2" @click="purgeRecordingsDirectory">
                    <i class="bi bi-exclamation-octagon me-1"></i>
                    Purge recordings
                </button>
            </div>
        </div>
        <!-- Discard and save buttons -->
        <div class="row mb-3">
            <div class="col">
                <button type="button" class="btn btn-outline-danger me-2" @click="resetForm">
                    <i class="bi bi-trash me-1"></i>
                    Discard
                </button>
                <button type="button" class="btn btn-primary me-2" @click="saveSettings">
                    <i class="bi bi-check2 me-1"></i>
                    Save
                </button>
                <button type="button" class="btn btn-outline-secondary float-end" @click="shutdown">
                    <i class="bi bi-power me-1"></i>
                    Shutdown
                </button>
                <button type="button" class="btn btn-outline-warning float-end me-2" @click="update">
                    <i class="bi bi-arrow-clockwise me-1"></i>
                    Update
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
                                    <label class="form-check-label" for="video0Radio">Video 0</label>
                                </div>
                                <div class="form-check form-check-inline">
                                    <input class="form-check-input" type="radio" name="inlineRadioOptions" id="video1Radio"
                                        value="1" v-model="configurator.currentVideoDevice" @change="resetConfigurator">
                                    <label class="form-check-label" for="video1Radio">Video 1</label>
                                </div>
                            </form>
                        </div>
                        <div class="col"><button type="reset" class="btn btn-primary me-2" @click="captureFrame">
                                <i class="bi bi-camera me-1"></i>
                                Capture frame
                            </button>
                        </div>
                        <div class="col"><button type="reset" class="btn btn-primary me-2" @click="previewWarped">
                                <i class="bi bi-bounding-box me-1"></i>
                                Preview warped
                            </button>
                        </div>
                    </div>
                    <div class="row mb-2">
                        <div class="col">
                            <!-- Image div -->
                            <div id="pointerDiv" class="border rounded"
                                :style="'background-image: url(' + configurator.capturedFrame + '); width: 100%; aspect-ratio: ' + getVideoAspectRatio(configurator.currentVideoDevice) + '; background-size: contain;'"
                                @click="imageClicked" ref="pointerDiv">

                                <!-- Spinner -->
                                <div class="h-100 d-flex align-items-center justify-content-center"
                                    :style="'visibility:' + configurator.spinnerVisibility + ';'">
                                    <div class="spinner-border" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </div>

                                <!-- Corner crosshairs -->
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
                    <!-- All the position entry boxes -->
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
                                    <span class="input-group-text">X</span>
                                    <input type="number" class="form-control" id="corner-tl-x" placeholder="0"
                                        v-model="configurator.corners[0][0]">
                                    <span class="input-group-text">Y</span>
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
                                    <span class="input-group-text">X</span>
                                    <input type="number" class="form-control" id="corner-tl-x" placeholder="0"
                                        v-model="configurator.corners[1][0]">
                                    <span class="input-group-text">Y</span>
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
                                    <span class="input-group-text">X</span>
                                    <input type="number" class="form-control" id="corner-tl-x" placeholder="0"
                                        v-model="configurator.corners[2][0]">
                                    <span class="input-group-text">Y</span>
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
                                    <span class="input-group-text">X</span>
                                    <input type="number" class="form-control" id="corner-tl-x" placeholder="0"
                                        v-model="configurator.corners[3][0]">
                                    <span class="input-group-text">Y</span>
                                    <input type="number" class="form-control" id="corner-tl-y" placeholder="0"
                                        v-model="configurator.corners[3][1]">
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline-danger me-2" data-bs-dismiss="modal" @click="">
                        <i class="bi bi-trash me-1"></i>
                        Discard
                    </button>
                    <button type="button" class="btn btn-primary me-2" @click="saveCorners">
                        <i class="bi bi-check2 me-1"></i>
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
import VideoSettings from './VideoSettings.vue';

export default {

    name: 'SettingsForm',
    data() {
        return {
            audioDevices: [],
            videoDevices: [],
            audioInputDevice: 0,
            customAudioDeviceCard: '',
            customAudioDeviceDev: '',
            endRecordingDelay: 1,
            stack: '',
            jobNameFormat: '',

            video0: {
                videoDevice: 0,
                resolutionX: '',
                resolutionY: '',
                enabled: false,
                corners: [[0, 0], [0, 0], [0, 0], [0, 0],],
                customVideoDevice: '',
                customVideoDeviceIndex: 0,
                streamcopy: false,
                framerate: 0,
                inputFormat: '',
                pixelFormat: '',
                focus: -1,
            },
            video1: {
                videoDevice: 0,
                resolutionX: '',
                resolutionY: '',
                enabled: false,
                corners: [[0, 0], [0, 0], [0, 0], [0, 0],],
                customVideoDevice: '',
                customVideoDeviceIndex: 0,
                streamcopy: false,
                framerate: 0,
                inputFormat: '',
                pixelFormat: '',
                focus: -1,
            },
            configurator: {
                capturedFrame: '',
                currentVideoDevice: 0,
                crosshairPositions: [[0, 0], [0, 0], [0, 0], [0, 0],],
                crosshairVisibility: ['hidden', 'hidden', 'hidden', 'hidden'],
                currentCorner: 0,
                corners: [[0, 0], [0, 0], [0, 0], [0, 0],],
                spinnerVisibility: 'hidden',
            },
            alert: {
                message: 'No response from backend',
                icon: 'exclamation-circle',
                color: 'danger',
                show: false,
            },
            files: {
                recordingDirectory: '',
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
                this.customAudioDeviceCard = response.data.custom_audio_device_card;
                this.customAudioDeviceDev = response.data.custom_audio_device_dev;
                this.endRecordingDelay = response.data.end_recording_delay;
                this.stack = response.data.stack;
                this.jobNameFormat = response.data.job_name_format;

                this.video0.videoDevice = response.data.video0.video_device[0];
                this.video0.resolutionX = response.data.video0.resolution[0];
                this.video0.resolutionY = response.data.video0.resolution[1];
                this.video0.enabled = response.data.video0.enabled;
                this.video0.customVideoDevice = response.data.video0.custom_video_device;
                this.video0.streamcopy = response.data.video0.streamcopy;
                this.video0.framerate = response.data.video0.framerate;
                this.video0.inputFormat = response.data.video0.input_format;
                this.video0.pixelFormat = response.data.video0.pixel_format;
                this.video0.focus = response.data.video0.focus;

                // If the custom video device index is -1, set it to blank so it looks better
                this.video0.customVideoDeviceIndex = response.data.video0.custom_video_device_index;
                if (this.video0.customVideoDeviceIndex == -1) {
                    this.video0.customVideoDeviceIndex = '';
                }

                this.video1.videoDevice = response.data.video1.video_device[0];
                this.video1.resolutionX = response.data.video1.resolution[0];
                this.video1.resolutionY = response.data.video1.resolution[1];
                this.video1.enabled = response.data.video1.enabled;
                this.video1.customVideoDevice = response.data.video1.custom_video_device;
                this.video1.streamcopy = response.data.video1.streamcopy;
                this.video1.framerate = response.data.video1.framerate;
                this.video1.inputFormat = response.data.video1.input_format;
                this.video1.pixelFormat = response.data.video1.pixel_format;
                this.video1.focus = response.data.video1.focus;

                // If the custom video device index is -1, set it to blank so it looks better
                this.video1.customVideoDeviceIndex = response.data.video1.custom_video_device_index;
                if (this.video1.customVideoDeviceIndex == -1) {
                    this.video1.customVideoDeviceIndex = '';
                }

                this.files.recordingDirectory = response.data.files.recording_directory;

            }).catch(error => {
                console.log(error);
            });
        },
        saveSettings() {
            // convert a blank custom video device index to -1
            var video0CustomVideoDeviceIndex = this.video0.customVideoDeviceIndex === '' ? -1 : this.video0.customVideoDeviceIndex;
            var video1CustomVideoDeviceIndex = this.video1.customVideoDeviceIndex === '' ? -1 : this.video1.customVideoDeviceIndex;

            axios.post('/settings', {
                audio_input_device: this.audioDevices[this.audioInputDevice],
                custom_audio_device_card: this.customAudioDeviceCard,
                custom_audio_device_dev: this.customAudioDeviceDev,
                end_recording_delay: this.endRecordingDelay,
                stack: this.stack,
                job_name_format: this.jobNameFormat,

                video0: {
                    video_device: this.videoDevices[this.video0.videoDevice],
                    resolution: [this.video0.resolutionX, this.video0.resolutionY],
                    enabled: this.video0.enabled,
                    custom_video_device: this.video0.customVideoDevice,
                    custom_video_device_index: video0CustomVideoDeviceIndex,
                    streamcopy: this.video0.streamcopy,
                    framerate: this.video0.framerate,
                    input_format: this.video0.inputFormat,
                    pixel_format: this.video0.pixelFormat,
                    focus: this.video0.focus,

                },
                video1: {
                    video_device: this.videoDevices[this.video1.videoDevice],
                    resolution: [this.video1.resolutionX, this.video1.resolutionY],
                    enabled: this.video1.enabled,
                    custom_video_device: this.video1.customVideoDevice,
                    custom_video_device_index: video1CustomVideoDeviceIndex,
                    streamcopy: this.video1.streamcopy,
                    framerate: this.video1.framerate,
                    input_format: this.video1.inputFormat,
                    pixel_format: this.video1.pixelFormat,
                    focus: this.video1.focus,
                },
                files: {
                    recording_directory: this.files.recordingDirectory,
                }

            }).then(response => {
                if (response.data.status == 'success') {
                    this.resetForm();
                    this.scrollToTop();

                    // Update the alert
                    this.alert.message = 'Settings saved';
                    this.alert.icon = 'check-circle';
                    this.alert.color = 'success';
                    this.alert.show = true;
                } else {
                    // Update the alert
                    this.alert.message = response.data.message;
                    this.alert.icon = 'exclamation-circle';
                    this.alert.color = 'danger';
                    this.alert.show = true;
                }

            }).catch(error => {
                console.log(error);

                // Update the alert
                this.alert.message = 'Error saving settings';
                this.alert.icon = 'exclamation-circle';
                this.alert.color = 'danger';
                this.alert.show = true;
            });
        },
        captureFrame() {
            this.configurator.spinnerVisibility = 'visible';
            axios.post('/capture_frame', {
                video_device: 'video' + this.configurator.currentVideoDevice,
            }).then(response => {
                this.configurator.spinnerVisibility = 'hidden';
                this.configurator.capturedFrame = response.data;

            }).catch(error => {
                console.log(error);
            });
        },
        crosshairOffset([x, y]) {
            return [x - 3, y + 48];
        },
        // This is very hacky, and I can't even say it works
        // imageClicked(event) {
        //     var currentCorner = parseInt(this.configurator.currentCorner);
        //     var modalOffsetX = this.$refs.configuratorModal.offsetLeft;
        //     var modalOffsetY = this.$refs.configuratorModal.offsetTop;
        //     var x = event.pageX - event.target.offsetLeft - modalOffsetX;
        //     var y = event.pageY - event.target.offsetTop - modalOffsetY - 64;
        //     this.configurator.crosshairPositions[currentCorner] = this.crosshairOffset([x, y]);
        //     this.configurator.crosshairVisibility[currentCorner] = 'visible';
        //     this.configurator.corners[currentCorner] = [x, y];
        // },
        imageClicked(event) {
            var currentCorner = parseInt(this.configurator.currentCorner);
            var x = event.offsetX;
            var y = event.offsetY;
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
                this.configurator.corners = this.unscaleCorners(this.video0.corners, this.video0.resolutionX);
            } else {
                this.configurator.corners = this.unscaleCorners(this.video1.corners, this.video1.resolutionX);
            }

            this.configurator.currentCorner = 0;

            // Set crosshair positions using offset
            for (var i = 0; i < this.configurator.crosshairPositions.length; i++) {
                this.configurator.crosshairPositions[i] = this.crosshairOffset(this.configurator.corners[i]);
            }

            // Set crosshair visibility
            if (JSON.stringify(this.configurator.corners) !== JSON.stringify([[0, 0], [0, 0], [0, 0], [0, 0]])) {
                this.configurator.crosshairVisibility = ['visible', 'visible', 'visible', 'visible'];
            } else {
                this.configurator.crosshairVisibility = ['hidden', 'hidden', 'hidden', 'hidden'];
            }
        },
        scaleCorners(unscaledCorners, resolutionX) {


            var scaledCorners = [];
            // Use the pointerDiv's pixel width to scale the corners to the original video resolution
            var pointerDivWidth = this.$refs.pointerDiv.offsetWidth;
            for (var i = 0; i < this.configurator.corners.length; i++) {
                scaledCorners[i] = [parseInt(unscaledCorners[i][0] * resolutionX / pointerDivWidth), parseInt(unscaledCorners[i][1] * resolutionX / pointerDivWidth)];
            }
            return scaledCorners;
        },
        unscaleCorners(scaledCorners, resolutionX) {
            // Reverse the scaling done in scaleCorners()
            var pointerDivWidth = this.$refs.pointerDiv.offsetWidth;
            var corners = [];
            for (var i = 0; i < scaledCorners.length; i++) {
                corners[i] = [parseInt(scaledCorners[i][0] * pointerDivWidth / resolutionX), parseInt(scaledCorners[i][1] * pointerDivWidth / resolutionX)];
            }
            return corners;
        },
        saveCorners() {
            if (parseInt(this.configurator.currentVideoDevice) === 0)
                var scaledCorners = this.scaleCorners(this.configurator.corners, this.video0.resolutionX);
            else if (parseInt(this.configurator.currentVideoDevice) === 1)
                var scaledCorners = this.scaleCorners(this.configurator.corners, this.video1.resolutionX);
            axios.post('/corners', {
                video_device: 'video' + this.configurator.currentVideoDevice,
                corners: scaledCorners,
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
        },
        previewWarped() {
            this.configurator.spinnerVisibility = 'visible';
            axios.post('/preview_warped', {
                video_device: 'video' + this.configurator.currentVideoDevice,
            }).then(response => {
                this.configurator.spinnerVisibility = 'hidden';
                this.configurator.capturedFrame = response.data;

            }).catch(error => {
                console.log(error);
            });
        },
        purgeRecordingsDirectory() {
            axios.post('/purge_recordings_directory').then(response => {
                if (response.data.status == 'success') {
                    // Update the alert
                    this.alert.message = 'Recordings purged';
                    this.alert.icon = 'check-circle';
                    this.alert.color = 'success';
                    this.alert.show = true;
                } else {
                    // Update the alert
                    this.alert.message = response.data.message;
                    this.alert.icon = 'exclamation-circle';
                    this.alert.color = 'danger';
                    this.alert.show = true;
                }

            }).catch(error => {
                console.log(error);

                // Update the alert
                this.alert.message = 'Error purging recordings';
                this.alert.icon = 'exclamation-circle';
                this.alert.color = 'danger';
                this.alert.show = true;
            });
            this.scrollToTop();
        },
        shutdown() {
            axios.post('/shutdown').then(response => {
                if (response.data.status == 'success') {
                    // Update the alert
                    this.alert.message = 'Shutdown initiated';
                    this.alert.icon = 'check-circle';
                    this.alert.color = 'success';
                    this.alert.show = true;
                } else {
                    // Update the alert
                    this.alert.message = response.data.message;
                    this.alert.icon = 'exclamation-circle';
                    this.alert.color = 'danger';
                    this.alert.show = true;
                }

            }).catch(error => {
                console.log(error);

                // Update the alert
                this.alert.message = 'Error initiating shutdown';
                this.alert.icon = 'exclamation-circle';
                this.alert.color = 'danger';
                this.alert.show = true;
            });
            this.scrollToTop();
        },
        scrollToTop() {
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
        },
        update() {
            axios.post('/update').then(response => {
                if (response.data.status == 'success') {
                    // Update the alert
                    this.alert.message = 'Update initiated';
                    this.alert.icon = 'check-circle';
                    this.alert.color = 'success';
                    this.alert.show = true;
                } else {
                    // Update the alert
                    this.alert.message = response.data.message;
                    this.alert.icon = 'exclamation-circle';
                    this.alert.color = 'danger';
                    this.alert.show = true;
                }
                this.scrollToTop();

            }).catch(error => {
                console.log(error);
            });
        },
    },
    mounted() {
        this.resetForm();
    },
}

</script>
