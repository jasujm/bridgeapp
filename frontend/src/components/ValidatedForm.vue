<template>
  <validation-observer ref="validationObserver" v-slot="{ handleSubmit }" slim>
    <b-form @submit.prevent="handleSubmit(submitHandlerWrapper)">
      <slot></slot>
    </b-form>
  </validation-observer>
</template>

<script lang="ts">
import { Vue, Component, Prop, Ref } from "vue-property-decorator";
import { ValidationObserver } from "vee-validate";
import { ValidationError } from "@/api/types";
import { AxiosError } from "axios";
import _ from "lodash";

@Component({
  components: {
    ValidationObserver,
  },
})
export default class ValidatedForm extends Vue {
  // This is ValidationObserver but I don't know how to use it with typescript
  // eslint-disable-next-line
  @Ref() private readonly validationObserver!: any;
  @Prop() private readonly submitHandler!: Function;
  @Prop() private readonly errorHandler?: Function;

  private async submitHandlerWrapper() {
    try {
      await this.submitHandler();
    } catch (err) {
      const axiosError = err as AxiosError;
      if (axiosError.isAxiosError && axiosError.response) {
        const status = axiosError.response.status;
        const data = axiosError.response.data;
        if (status == 422 && _.isArray(data.detail)) {
          this.setErrorsFromResponse(data.detail);
        } else if (this.errorHandler) {
          this.errorHandler(axiosError);
        } else {
          throw err;
        }
      } else {
        throw err;
      }
    }
  }

  public reset() {
    this.validationObserver.reset();
  }

  public setError(field: string, error: string) {
    this.validationObserver.setErrors({ [field]: error });
  }

  public setErrorsFromResponse(errors: Array<ValidationError>) {
    const errors_ = _.fromPairs(
      errors.map(({ loc, msg }) => [_.last(loc), msg])
    );
    this.validationObserver.setErrors(errors_);
  }
}
</script>
