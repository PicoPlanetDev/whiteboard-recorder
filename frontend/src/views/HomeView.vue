<script setup>
import ButtonGroup from '../components/ButtonGroup.vue';
import Footer from '../components/Footer.vue';
import Header from '../components/Header.vue';
</script>

<template>
  <div class="col-lg-8 mx-auto p-4 py-md-5">
    <!-- Header -->
    <Header />

    <!-- Alerts -->

    <main>
      <div class="row">
        <div class="col-md-8">
          <h1>Control panel</h1>
          <p class="fs-5">Start, stop, and download whiteboard recordings from this page.
            Bookmark the below IP address and port for easy access.</p>
          <p class="fs-6 font-monospace">Connected to server at {{ ip_address }}</p>
        </div>
        <div class="col">
          <img :src="qrCodeUrl" alt="QR code for URL" height="200" class="rounded">
        </div>
      </div>

      <div class="mb-5">
        <ButtonGroup />
      </div>
    </main>

    <Footer />
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'HomeView',
  computed: {
    qrCodeUrl() {
      return axios.defaults.baseURL + '/get_qr_code';
    },
    ip_address() {
      return window.location.href;
    },
  },
}
</script>
