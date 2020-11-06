<template>
<div class="login">
    <b-card>
        <b-card-text>
            Start by “logging in”. As of yet, there is no actual authentication,
            so anyone can claim any username at any time. The application just
            uses it to distinguish players from each other. The username will
            not be saved. All data collected by the server is pseudonymized.
        </b-card-text>
        <b-form-group label-for="username" label="Username">
            <b-form-input id="username" v-model="username"></b-form-input>
        </b-form-group>
        <b-button variant="primary" v-on:click="login()">Login</b-button>
    </b-card>
</div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class Login extends Vue {
    username = "";

    login() {
        this.$store.dispatch("login", this.username);
    }
}
</script>
