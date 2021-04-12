<template>
    <validation-observer ref="validationObserver" v-slot="{ handleSubmit }" slim>
        <b-form @submit.prevent="handleSubmit(submitHandler)">
            <slot></slot>
        </b-form>
    </validation-observer>
</template>

<script lang="ts">
    import { Vue, Component, Prop, Ref } from "vue-property-decorator"
import { ValidationObserver } from "vee-validate";
import { ValidationError } from "@/api/types"
import _ from "lodash"

@Component({
    components: {
        ValidationObserver,
    }
})
export default class ValidatedForm extends Vue {
    // This is ValidationObserver but I don't know how to use it with typescript
    // eslint-disable-next-line
    @Ref() private readonly validationObserver!: any;
    @Prop() private readonly submitHandler!: Function;

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
