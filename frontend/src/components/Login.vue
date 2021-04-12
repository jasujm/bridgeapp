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
        <ValidatedForm ref="loginForm" :submitHandler="login">
            <ValidatedFormGroup vid="username" name="Username" rules="required|min:2|max:31" v-slot="{ labelId, state }">
                <b-form-input
                    :id="labelId"
                    :state="state"
                    v-model="username">
                </b-form-input>
            </ValidatedFormGroup>
            <b-button type="submit" variant="primary">Login</b-button>
        </ValidatedForm>
    </b-modal>
    <b-button v-if="!$store.getters.isLoggedIn" v-b-modal.login-modal>Login</b-button>
</div>
</template>

<script lang="ts">
import { Vue, Component, Ref } from "vue-property-decorator"
import ValidatedForm from "./ValidatedForm.vue"
import ValidatedFormGroup from "./ValidatedFormGroup.vue"
import { AxiosError } from "axios"
import { ValidationProvider } from "vee-validate";
import _ from "lodash"

@Component({
    components: {
        ValidatedForm,
        ValidationProvider,
        ValidatedFormGroup,
    }
})
export default class Login extends Vue {
    @Ref() private readonly loginForm!: ValidatedForm;
    private readonly username = "";

    private get testing() {
        // Ugh...
        return process.env.NODE_ENV == "test";
    }

    async login() {
        const api = this.$store.state.api;
        let id: string | undefined;
        try {
            ({ id } = await api.createPlayer(this.username));
        } catch (err) {
            const axiosError = err as AxiosError;
            if (axiosError.isAxiosError && axiosError.response) {
                const status = axiosError.response.status;
                const data = axiosError.response.data;
                if (status == 409) {
                    ({ id } = await api.getPlayer(this.username));
                } else if (status == 422 && _.isArray(data.detail)) {
                    this.loginForm.setErrorsFromResponse(data.detail);
                }
            }
        }
        if (id) {
            this.$store.dispatch("login", id);
        }
    }
}
</script>
