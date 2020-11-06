<template>
<div class="call-panel">
    <b-button v-for="call in allowedCalls" :key="callKey(call)" class="m-1" variant="outline-dark" @click="makeCall(call)">
        <CallDisplay :type="call.type" :bid="call.bid" />
    </b-button>
</div>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator"
import CallDisplay from "./CallDisplay.vue"
import { callKey } from "@/utils"
import { Call } from "@/api/types"

@Component({
    components: {
        CallDisplay,
    }
})
export default class CallPanel extends Vue {
    @Prop() private readonly gameUuid!: string;
    @Prop({ default: [] }) private readonly allowedCalls!: Array<Call>;
    private callKey = callKey;

    private async makeCall(call: Call) {
        if (this.gameUuid) {
            await this.$store.state.api.makeCall(this.gameUuid, call);
        }
    }
}
</script>
