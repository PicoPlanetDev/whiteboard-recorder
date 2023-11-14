<script setup>
//import { RouterLink, RouterView } from 'vue-router'
import Alert from './Alert.vue'
</script>

<template>
    <footer class="py-4 text-muted border-top d-flex align-items-center">
        Created by Sigmond Kukla &middot; &copy; {{ new Date().getFullYear() }}
        <Alert color="success" icon="activity" message="Connected" class="ms-auto"/>
    </footer>
</template>

<script>
export default {
    name: 'Footer',
}
</script>