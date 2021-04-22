<template>
<div class="account">
    <h1>Account settings: {{ player && player.username }}</h1>
    <h2>Change password</h2>
    <ValidatedForm ref="changePasswordForm" :submitHandler="changePassword" :errorHandler="changePasswordError">
        <b-alert variant="success" :show="passwordChanged">Password changed</b-alert>
        <ValidatedFormGroup vid="currentPassword" name="Current password" rules="required" v-slot="{ labelId, state }">
            <b-form-input
                :id="labelId"
                :state="state"
                type="password"
                v-model="currentPassword"
                name="current_password">
            </b-form-input>
        </ValidatedFormGroup>
        <ValidatedFormGroup vid="newPassword" name="New password" rules="required" v-slot="{ labelId, state }">
            <b-form-input
                :id="labelId"
                :state="state"
                type="password"
                v-model="newPassword"
                name="newPassword">
            </b-form-input>
        </ValidatedFormGroup>
        <ValidatedFormGroup name="Confirm password" rules="required|confirmed:newPassword" v-slot="{ labelId, state }">
            <b-form-input
                :id="labelId"
                :state="state"
                type="password"
                v-model="passwordConfirm"
                name="password_confirm">
            </b-form-input>
        </ValidatedFormGroup>
        <b-button type="submit" variant="primary">Submit</b-button>
    </ValidatedForm>
</div>
</template>

<script lang="ts">
import { Vue, Component, Watch, Ref } from "vue-property-decorator"
import { Player } from "@/api/types"
import ValidatedForm from "@/components/ValidatedForm.vue"
import ValidatedFormGroup from "@/components/ValidatedFormGroup.vue"
import { AxiosError } from "axios"

@Component({
    components: {
        ValidatedForm,
        ValidatedFormGroup,
    }
})
export default class Account extends Vue {
    @Ref() private readonly changePasswordForm!: ValidatedForm;
    private player: Player | null = null;
    private currentPassword = "";
    private newPassword = "";
    private passwordConfirm = "";
    private passwordChanged = false;

    @Watch("$store.getters.isLoggedIn", { immediate: true })
    async onLogin(isLoggedIn: boolean) {
        if (isLoggedIn) {
            this.player = await this.$store.state.api.getMe();
        } else {
            this.player = null;
        }
    }

    async changePassword() {
        await this.$store.state.api.changePassword(
            this.currentPassword, this.newPassword
        );
        this.currentPassword = "";
        this.newPassword = "";
        this.passwordConfirm = "";
        this.changePasswordForm.reset();
        this.passwordChanged = true;
    }

    changePasswordError(err: AxiosError) {
        if (err.response && err.response.status == 401) {
            this.changePasswordForm.setError(
                "currentPassword", "Incorrect password"
            );
        }
    }
}
</script>
