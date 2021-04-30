<template>
  <validation-provider
    :vid="vid"
    :name="name"
    :rules="rules"
    v-slot="validationContext"
  >
    <b-form-group
      :label-for="noLabel ? undefined : labelId"
      :label="noLabel ? undefined : name"
      :invalid-feedback="validationContext.errors[0]"
      :state="getValidationState(validationContext)"
    >
      <slot
        v-bind:state="getValidationState(validationContext)"
        v-bind:labelId="labelId"
      >
      </slot>
    </b-form-group>
  </validation-provider>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator";
import { extend } from "vee-validate";
import { required, min, max, confirmed } from "vee-validate/dist/rules";
import { validate as validateUuid } from "uuid";
import { ValidationProvider } from "vee-validate";

extend("required", {
  ...required,
  message: "{_field_} is required",
});

extend("min", {
  ...min,
  message: "{_field_} too short",
});

extend("max", {
  ...max,
  message: "{_field_} too long",
});

extend("confirmed", {
  ...confirmed,
  message: "{_field_} must match",
});

extend("uuid", function (value: string) {
  if (validateUuid(value)) {
    return true;
  }
  return "{_field_} must be a valid UUID";
});

@Component({
  components: {
    ValidationProvider,
  },
})
export default class ValidatedFormGroup extends Vue {
  @Prop() private readonly name!: string;
  @Prop({ type: Boolean, default: false }) private readonly noLabel!: boolean;
  @Prop() private readonly rules!: string;
  @Prop() private readonly vid?: string;

  private getValidationState({
    dirty,
    validated,
    valid = null,
  }: {
    dirty: boolean;
    validated: boolean;
    valid: boolean | null;
  }) {
    return dirty || validated ? valid : null;
  }

  private get labelId() {
    return this.$id(this.name.replace(/\s+/, ""));
  }
}
</script>
