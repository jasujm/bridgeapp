<template>
<ValidatedForm ref="signupForm" :submitHandler="signup">
    <ValidatedFormGroup vid="username" name="Username" rules="required|min:2|max:31" v-slot="{ labelId, state }">
        <b-form-input
            :id="labelId"
            :state="state"
            v-model="username"
            name="username">
        </b-form-input>
    </ValidatedFormGroup>
    <ValidatedFormGroup name="Password" rules="required" v-slot="{ labelId, state }">
        <b-form-input
            :id="labelId"
            :state="state"
            type="password"
            v-model="password"
            name="password">
        </b-form-input>
    </ValidatedFormGroup>
    <ValidatedFormGroup name="Confirm password" rules="required|confirmed:Password" v-slot="{ labelId, state }">
        <b-form-input
            :id="labelId"
            :state="state"
            type="password"
            v-model="passwordConfirm"
            name="password_confirm">
        </b-form-input>
    </ValidatedFormGroup>
    <b-button type="submit" variant="primary">Sign up</b-button>
</ValidatedForm>
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
export default class SignupForm extends Vue {
    @Ref() private readonly signupForm!: ValidatedForm;
    private readonly username = "";
    private readonly password = "";
    private readonly passwordConfirm = "";

    async signup() {
        const api = this.$store.state.api;
        try {
            await api.createPlayer(this.username, this.password);
        } catch (err) {
            const axiosError = err as AxiosError;
            if (axiosError.isAxiosError && axiosError.response) {
                const status = axiosError.response.status;
                const data = axiosError.response.data;
                if (status == 409) {
                    this.signupForm.setError("username", data.detail);
                } else if (status == 422 && _.isArray(data.detail)) {
                    this.signupForm.setErrorsFromResponse(data.detail);
                }
            }
            return;
        }
        await this.$store.dispatch("login", { username: this.username, password: this.password });
    }
}
</script>
