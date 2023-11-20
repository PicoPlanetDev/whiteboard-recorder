<script setup>
import Footer from '../components/Footer.vue';
import Header from '../components/Header.vue';
import Jobs from '../components/Jobs.vue';
import RecordingButton from '../components/RecordingButton.vue';
</script>

<template>
  <div class="col-lg-8 mx-auto p-4 py-md-5">
    <!-- Header -->
    <Header />

    <!-- TODO: Alerts -->

    <main>
      <div class="row mb-3">
        <div class="col-md-8">
          <h1>Control panel</h1>
          <p class="fs-5">Start, stop, and download whiteboard recordings from this page.
            Bookmark the below IP address and port for easy access.</p>
          <p class="fs-6 font-monospace">Connected to server at <a :href="'http://' + ip_address + ':5173/'">http://{{
            ip_address }}:5173/</a></p>
        </div>
        <!-- QR code -->
        <div class="col">
          <img :src="qrCodeUrl" alt="QR code for URL" height="150" class="rounded-4 float-end">
        </div>
      </div>

      <div class="mb-3">
        <RecordingButton />
      </div>
      <hr>
      <div>
        <Jobs />
      </div>
    </main>

    <Footer />
  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'HomeView',
  data() {
    return {
      ip_address: '',
    };
  },
  computed: {
    qrCodeUrl() {
      return axios.defaults.baseURL + '/get_qr_code';
    },
  },
  methods: {
    getUrl() {
      axios.get('/get_local_ip')
        .then((response) => {
          this.ip_address = response.data.ip;
        })
        .catch((error) => {
          console.log(error);
        });
    },
  },
  mounted() {
    this.getUrl();
  },
};
</script>
