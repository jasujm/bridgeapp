<template>
<div class="login" v-b-modal.login-modal>
    Log in / Sign up
    <b-modal
        id="login-modal"
        :visible="!$store.getters.isLoggedIn"
        title="Welcome to contract bridge!"
        hide-footer>
        <p>Log in or create an account to continue.</p>
        <b-tabs content-class="mt-3">
            <b-tab title="Log in"><LoginForm /></b-tab>
            <b-tab title="Sign up"><SignupForm /></b-tab>
        </b-tabs>
    </b-modal>
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
