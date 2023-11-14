<template>
    <div class="mb-3 alert d-flex align-items-center" :class="`alert-${color}`" role="alert">
        <i class="bi flex-shrink-0 me-2" :class="`bi-${icon}`"></i>
        {{ message }}
    </div>
</template>

<script>
export default {
    name: 'Alert',
    props: {
        message: {
            type: String,
            required: true
        },
        icon: {
            type: String,
            default: 'info-circle'
        },
        color: {
            type: String,
            default: 'secondary'
        },
    },
}
</script>