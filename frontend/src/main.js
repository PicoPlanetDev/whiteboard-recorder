import './assets/main.css'

// Bootstrap
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Bootstrap Icons
import 'bootstrap-icons/font/bootstrap-icons.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Axios base URL
import axios from 'axios'
if (import.meta.env.VITE_API_ENDPOINT === "default") {
    axios.defaults.baseURL = window.location.href.split(':5173')[0] + ":5000/api";
}
else {
    axios.defaults.baseURL = import.meta.env.VITE_API_ENDPOINT;
};

const app = createApp(App)

app.use(router)

app.mount('#app')
