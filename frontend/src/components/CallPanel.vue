<template>
<div class="call-panel">
    <b-button
        v-for="call in allowedCalls"
        :key="callKey(call)"
        class="m-1"
        variant="outline-dark"
        @click="$emit('call', call)">
        <CallDisplay :type="call.type" :bid="call.bid" />
    </b-button>
</div>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator"
import CallDisplay from "./CallDisplay.vue"
import { Call } from "@/api/types"

@Component({
    components: {
        CallDisplay,
    }
})
export default class CallPanel extends Vue {
    @Prop({ default: () => [] }) private readonly allowedCalls!: Array<Call>;

    callKey(call: Call) {
        let ret: Array<string> = [call.type];
        if (call.bid) {
            ret = ret.concat([String(call.bid.level), call.bid.strain]);
        }
        return ret.join("-");
    }
}
</script>
