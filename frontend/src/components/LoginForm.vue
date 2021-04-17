<template>
<ValidatedForm ref="loginForm" :submitHandler="login">
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
    <b-button type="submit" variant="primary">Log in</b-button>
</ValidatedForm>
</template>

<script lang="ts">
import { Vue, Component, Ref } from "vue-property-decorator"
import ValidatedForm from "./ValidatedForm.vue"
import ValidatedFormGroup from "./ValidatedFormGroup.vue"

@Component({
    components: {
        ValidatedForm,
        ValidatedFormGroup,
    }
})
export default class LoginForm extends Vue {
    @Ref() private readonly loginForm!: ValidatedForm;
    private readonly username = "";
    private readonly password = "";

    async login() {
        await this.$store.dispatch("login", { username: this.username, password: this.password });
        if (!this.$store.state.isLoggedIn) {
            this.loginForm.setError("username", "Incorrect username or password");
        }
    }
}
</script>
