import { extend } from 'vee-validate';
import { required } from 'vee-validate/dist/rules';
import { validate as validateUuid } from "uuid"
import Vue from 'vue'
import Component from 'vue-class-component'
import { ValidationProvider } from 'vee-validate';

extend('required', {
    ...required,
    message: "The field is required",
});

extend('uuid', function(value) {
    if (validateUuid(value)) {
        return true;
    }
    return "The field must be a valid UUID";
});

@Component({
    components: {
        ValidationProvider,
    }
})
export class ValidationMixin extends Vue {
    getValidationState({ dirty, validated, valid = null }: { dirty: boolean; validated: boolean; valid: boolean | null }) {
        return dirty || validated ? valid : null;
    }
}
