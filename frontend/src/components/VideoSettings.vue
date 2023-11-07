<template>
    <div class="col border rounded">
        <!-- Header and enabled -->
        <div class="row">
            <div class="col-auto fs-5">Video {{ videoNumber }}</div>
            <div class="col">
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" role="switch" id="videoCheckSwitch"
                        v-model="videoData.enabled">
                    <label class="form-check-label" for="videoCheckSwitch">Video {{ videoNumber }} enabled</label>
                </div>
            </div>
        </div>

        <div class="row" v-if="videoData.enabled">
            <!-- Video 0 Device -->
            <div class="mb-3">
                Video device
                <select class="form-select" v-model="videoData.videoDevice" @select="updateVideo">
                    <option disabled value="">Please select one</option>
                    <option v-for="device in videoDevices" :key="device[0]" :value="device[0]">
                        {{ device[1] }}
                    </option>
                </select>
            </div>
            <!-- Video 0 Custom Devices -->
            <div class="mb-3">
                Custom video device (disabled if blank)
                <div class="input-group">
                    <span class="input-group-text">Name</span>
                    <input type="text" class="form-control" placeholder="" aria-label="Custom video device name"
                        v-model="videoData.customVideoDevice" @input="updateVideo">
                    <span class="input-group-text">Index</span>
                    <input type="number" class="form-control" placeholder="" aria-label="Custom video device index"
                        v-model="videoData.customVideoDeviceIndex" @input="updateVideo">
                </div>
            </div>
            <!-- Video 0 Stream copy -->
            <div class="mb-2">
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" role="switch" id="videoStreamCopyCheckSwitch"
                        v-model="videoData.streamcopy" @input="updateVideo">
                    <label class="form-check-label" for="videoStreamCopyCheckSwitch">Stream copy</label>
                </div>
            </div>
            <!-- Video 0 resolution -->
            <div class="mb-3">
                <label for="resolution-x" class="form-label">Video resolution</label>
                <div class="input-group">
                    <span class="input-group-text">X</span>
                    <input type="number" class="form-control" id="resolution-x" placeholder="1920"
                        v-model="videoData.resolutionX" @input="updateVideo">
                    <span class="input-group-text">Y</span>
                    <input type="number" class="form-control" id="resolution-y" placeholder="1080"
                        v-model="videoData.resolutionY" @input="updateVideo">
                </div>
            </div>
            <!-- Video 0 Framerate -->
            <div class="mb-3">
                <label for="videoFramerateInput" class="form-label">Framerate</label>
                <input type="number" id="videoFramerateInput" class="form-control" v-model="videoData.framerate"
                    @input="updateVideo">
            </div>
            <!-- Video 0 Input Format -->
            <div class="mb-3">
                <label for="inputFormatInput" class="form-label">Input format</label>
                <input type="text" id="inputFormatInput" class="form-control" aria-describedby="inputFormatInputHelpBlock"
                    v-model="videoData.inputFormat" @input="updateVideo">
                <div id="inputFormatInputHelpBlock" class="form-text">
                    Video device input format, commonly <span class="font-monospace">mjpeg</span> or <span
                        class="font-monospace">yuyv422</span>.
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "VideoSettings",
    props: {
        videoDevices: {
            type: Array,
            required: true
        },
        video: {
            type: Object,
            required: true
        },
        videoNumber: {
            type: Number,
            required: true
        }
    },
    data() {
        return {
            videoData: this.video
        }
    },
    methods: {
        updateVideo() {
            this.$emit('update-video', this.videoData);
        }
    },
}
</script>