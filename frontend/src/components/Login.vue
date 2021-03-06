<template>
<div class="login">
    <b-modal
        id="login-modal"
        :static="testing"
        :visible="!$store.getters.isLoggedIn"
        title="Welcome to contract bridge!"
        hide-footer>
        <p>
            Choose a name for yourself. There is no actual registration or
            authentication, so anyone can claim any username at any time.
        </p>
        <validation-observer v-slot="{ handleSubmit }" slim>
            <b-form @submit.stop.prevent="handleSubmit(login)">
                <validation-provider name="Username" rules="required|min:2|max:15" v-slot="validationContext">
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
                <b-button type="submit" variant="primary">Login</b-button>
            </b-form>
        </validation-observer>
    </b-modal>
    <b-button v-if="!$store.getters.isLoggedIn" v-b-modal.login-modal>Login</b-button>
</div>
</template>

<script lang="ts">
import Component, { mixins } from "vue-class-component";
import { ValidationMixin } from "./validation";
import { AxiosError } from "axios"

@Component
export default class Login extends mixins(ValidationMixin) {
    private readonly username = "";

    private get testing() {
        // Ugh...
        return process.env.NODE_ENV == "test";
    }

    async login() {
        const api = this.$store.state.api;
        let id: string | undefined;
        try {
            ({ id } = await api.getPlayer(this.username));
        } catch (err) {
            const axiosError = err as AxiosError;
            if (axiosError.isAxiosError && axiosError.response && axiosError.response.status == 404) {
                // TODO: display errors if creating player fails
                ({ id } = await api.createPlayer(this.username));
            }
        }
        if (id) {
            this.$store.dispatch("login", id);
        }
    }
}
</script>
