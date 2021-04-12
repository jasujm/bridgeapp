<template>
<div class="login">
    <b-modal
        id="login-modal"
        :visible="!$store.getters.isLoggedIn"
        title="Welcome to contract bridge!"
        hide-footer>
        <p>Login or create an account to continue.</p>
        <b-tabs content-class="mt-3">
            <b-tab title="Login"><LoginForm /></b-tab>
            <b-tab title="Sign up"><SignupForm /></b-tab>
        </b-tabs>
    </b-modal>
    <b-button v-if="!$store.getters.isLoggedIn" v-b-modal.login-modal>Login</b-button>
</div>
</template>

<script lang="ts">
import Component from "vue-class-component"
import Vue from "vue"
import LoginForm from "./LoginForm.vue"
import SignupForm from "./SignupForm.vue"

@Component({
    components: {
        LoginForm,
        SignupForm,
    }
})
export default class Login extends Vue {}
</script>
