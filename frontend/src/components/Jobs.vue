<template>
    <div class="row mb-3">
        <div class="col">
            <h4>Jobs</h4>
        </div>
        <div class="col">
            <button type="button" class="btn btn-danger float-end" @click="clearFinishedJobs">
                <i class="bi bi-trash"></i>
                Clear finished
            </button>
            <button type="button" class="btn btn-success me-2 float-end" @click="runAllJobs">
                <i class="bi bi-play"></i>
                Run all
            </button>
            <button type="button" class="btn btn-secondary me-2 float-end" @click="getJobs">
                <i class="bi bi-arrow-clockwise"></i>
                Refresh
            </button>
        </div>
    </div>
    <div class="row mb-3">
        <div class="container-fluid">
            <!-- Table of jobs where each row has the name, message, and run, delete, and download actions -->
            <table class="table" v-if="jobs.length > 0">
                <thead>
                    <tr>
                        <th scope="col">Name</th>
                        <th scope="col">Status</th>
                        <th scope="col"><span class="float-end">Actions</span></th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="job in jobs" :key="job.name">
                        <td>{{ job.name }}</td>
                        <td>
                            <span class="me-2">
                                {{ job.message }}
                            </span>
                            <div class="spinner-border-sm spinner-border" role="status" v-if="job.started && !job.finished">
                                <span class="visually-hidden">Processing...</span>
                            </div>
                        </td>
                        <td>
                            <div class="btn-group float-end" role="group">
                                <button type="button" class="btn btn-sm btn-success" @click="runJob(job.name)">
                                    <i class="bi bi-play"></i>
                                </button>

                                <button type="button" class="btn btn-sm btn-danger" @click="deleteJob(job.name)">
                                    <i class="bi bi-trash"></i>
                                </button>
                                <button type="button" class="btn btn-sm btn-primary" @click="downloadJob(job.name)"
                                    :disabled="!job.finished">
                                    <i class="bi bi-download"></i>
                                    Download video
                                </button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
            <!-- If there are no jobs, display a message -->
            <div v-else>
                <p class="fs-5">No jobs found.</p>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
export default {
    data() {
        return {
            jobs: [],
        };
    },
    methods: {
        getJobs() {
            axios.get('/jobs')
                .then((response) => {
                    this.jobs = response.data.jobs;
                })
                .catch((error) => {
                    console.log(error);
                });
        },
        runJob(name) {
            axios.post('/jobs', { action: "run", job_name: name })
                .then((response) => {
                    this.getJobs();
                })
                .catch((error) => {
                    console.log(error);
                });
        },
        deleteJob(name) {
            axios.post('/jobs', { action: "remove", job_name: name })
                .then((response) => {
                    this.getJobs();
                })
                .catch((error) => {
                    console.log(error);
                });
        },
        runAllJobs() {
            axios.post('/jobs', { action: "run_all" })
                .then((response) => {
                    this.getJobs();
                })
                .catch((error) => {
                    console.log(error);
                });
        },
        clearFinishedJobs() {
            axios.post('/jobs', { action: "clear_finished" })
                .then((response) => {
                    this.getJobs();
                })
                .catch((error) => {
                    console.log(error);
                });
        },
        downloadJob(name) {
            axios({
                url: '/jobs',
                method: 'POST',
                responseType: 'blob', // important
                data: { action: "download", job_name: name }
            }).then((response) => {
                // witchcraft to download the file
                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', name + '.mp4');
                document.body.appendChild(link);
                link.click();
            })
        }
    },
    mounted() {
        this.getJobs();
        this.jobInterval = setInterval(() => {
            this.getJobs();
        }, 5000);
    },
    beforeUnmount() {
        clearInterval(this.jobInterval);
    }
}
</script>