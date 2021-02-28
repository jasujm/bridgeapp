import { extend } from "vee-validate";
import { required, min, max } from "vee-validate/dist/rules";
import { validate as validateUuid } from "uuid"
import Vue from "vue"
import Component from "vue-class-component"
import { ValidationObserver, ValidationProvider } from "vee-validate";

extend("required", {
    ...required,
    message: "{_field_} is required",
});

extend("min", {
    ...min,
    message: "{_field_} too short"
});

extend("max", {
    ...max,
    message: "{_field_} too long"
});

extend("uuid", function(value: string) {
    if (validateUuid(value)) {
        return true;
    }
    return "The field must be a valid UUID";
});

@Component({
    components: {
        ValidationObserver,
        ValidationProvider,
    }
})
export class ValidationMixin extends Vue {
    getValidationState({ dirty, validated, valid = null }: { dirty: boolean; validated: boolean; valid: boolean | null }) {
        return dirty || validated ? valid : null;
    }
}
