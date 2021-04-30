<template>
  <ValidatedForm
    ref="signupForm"
    :submitHandler="signup"
    :errorHandler="signupError"
  >
    <ValidatedFormGroup
      vid="username"
      name="Username"
      rules="required|min:2|max:31"
      v-slot="{ labelId, state }"
    >
      <b-form-input
        :id="labelId"
        :state="state"
        v-model="username"
        name="username"
      >
      </b-form-input>
    </ValidatedFormGroup>
    <ValidatedFormGroup
      vid="password"
      name="Password"
      rules="required"
      v-slot="{ labelId, state }"
    >
      <b-form-input
        :id="labelId"
        :state="state"
        type="password"
        v-model="password"
        name="password"
      >
      </b-form-input>
    </ValidatedFormGroup>
    <ValidatedFormGroup
      name="Confirm password"
      rules="required|confirmed:password"
      v-slot="{ labelId, state }"
    >
      <b-form-input
        :id="labelId"
        :state="state"
        type="password"
        v-model="passwordConfirm"
        name="password_confirm"
      >
      </b-form-input>
    </ValidatedFormGroup>
    <ValidatedFormGroup
      name="Accepting terms and conditions and privacy policy"
      :rules="{ required: { allowFalse: false } }"
      v-slot="{ state }"
      no-label
    >
      <b-form-checkbox
        :state="state"
        v-model="termsAccepted"
        name="terms_accepted"
      >
        Accept
        <a href="https://www.websitepolicies.com/policies/view/RTZfOT2W"
          >terms and conditions</a
        >
        and
        <a href="https://www.websitepolicies.com/policies/view/STbelXSV"
          >privacy policy</a
        >
      </b-form-checkbox>
    </ValidatedFormGroup>
    <b-button type="submit" variant="primary">Sign up</b-button>
  </ValidatedForm>
</template>

<script lang="ts">
import { Vue, Component, Ref } from "vue-property-decorator";
import ValidatedForm from "./ValidatedForm.vue";
import ValidatedFormGroup from "./ValidatedFormGroup.vue";
import { AxiosError } from "axios";

@Component({
  components: {
    ValidatedForm,
    ValidatedFormGroup,
  },
})
export default class SignupForm extends Vue {
  @Ref() private readonly signupForm!: ValidatedForm;
  private readonly username = "";
  private readonly password = "";
  private readonly passwordConfirm = "";
  private readonly termsAccepted = false;

  private async signup() {
    await this.$store.state.api.createPlayer(this.username, this.password);
    await this.$store.dispatch("login", {
      username: this.username,
      password: this.password,
    });
  }

  private signupError(err: AxiosError) {
    if (err.response && err.response.status == 409) {
      this.signupForm.setError("username", err.response.data.detail);
    }
  }
}
</script>
