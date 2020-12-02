<template>
<div class="error-display">
    <b-alert :variant="severity" v-model="showError" dismissible>{{ message }}</b-alert>
</div>
</template>

<script lang="ts">
import { Vue, Component, Prop, Watch } from "vue-property-decorator"
import { ErrorSeverity } from "@/api/types"

@Component
export default class ErrorDisplay extends Vue {
    @Prop({ default: ErrorSeverity.danger }) private readonly severity!: ErrorSeverity;
    @Prop({ default: "" }) private readonly message!: string;
    private showError = false;

    @Watch("message")
    private messageChanged(message: string) {
        this.showError = Boolean(message);
    }
}
</script>
