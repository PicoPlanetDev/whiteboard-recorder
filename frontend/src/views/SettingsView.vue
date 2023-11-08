<script setup>
import { RouterLink, RouterView } from 'vue-router'
import Header from '../components/Header.vue';
import Footer from '../components/Footer.vue';
import SettingsForm from '../components/SettingsForm.vue';
</script>

<template>
  <div class="col-lg-8 mx-auto p-4 py-md-5">
    <!-- Header -->
    <Header />

    <!-- Alerts -->

    <!-- Content -->
    <main>
      <SettingsForm />
    </main>

    <Footer />
  </div>
</template>
