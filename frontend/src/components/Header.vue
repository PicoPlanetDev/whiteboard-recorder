<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
    <header class="d-flex align-items-center pb-3 mb-5 border-bottom">
        <RouterLink to="/" class="fs-4 text-body text-decoration-none">
            <img src="favicon/favicon.svg" width="40" class="me-2" alt="Whiteboard recorder logo">
            <span class="fs-4">Whiteboard Recorder</span>
        </RouterLink>
        <RouterLink to="/" class="ms-auto fs-4 text-body text-decoration-none me-5">
                <i class="bi bi-house-fill"></i>
                Home
            </RouterLink>
        <RouterLink to="/settings" class="fs-4 text-body text-decoration-none">
            <i class="bi bi-gear-fill"></i>
            Settings
        </RouterLink>
    </header>
</template>

<script>
export default {
    name: 'Header',
}
</script>