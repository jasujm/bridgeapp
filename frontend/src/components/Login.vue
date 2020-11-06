<template>
<div class="login">
    <b-card>
        <b-card-text>
            Start by “logging in”. As of yet, there is no actual authentication,
            so anyone can claim any username at any time. The application just
            uses it to distinguish players from each other. The username will
            not be saved. All data collected by the server is pseudonymized.
        </b-card-text>
        <validation-provider name="Username" rules="required" v-slot="validationContext">
            <b-form-group label-for="username" label="Username">
                <b-form-input
                    id="username"
                    v-model="username"
                    :state="getValidationState(validationContext)"
                    aria-describedby="username-feedback"></b-form-input>
                <b-form-invalid-feedback id="username-feedback">
                    {{ validationContext.errors[0] }}
                </b-form-invalid-feedback>
            </b-form-group>
        </validation-provider>
        <b-button variant="primary" @click="login()">Login</b-button>
    </b-card>
</div>
</template>

<script lang="ts">
import Component, { mixins } from 'vue-class-component'
import { ValidationMixin } from './validation';

@Component
export default class Login extends mixins(ValidationMixin) {
    private readonly username = "";

    login() {
        this.$store.dispatch("login", this.username);
    }
}
</script>
