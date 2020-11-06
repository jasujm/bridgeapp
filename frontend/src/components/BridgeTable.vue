<template>
<div class="bridge-table">
    <Bidding :calls="deal.calls" />
    <CallPanel :gameUuid="gameUuid" :allowedCalls="self.allowedCalls" />
</div>
</template>

<script lang="ts">
import { Vue, Component, Prop, Watch } from "vue-property-decorator"
import Bidding from "./Bidding.vue"
import CallPanel from "./CallPanel.vue"
import { Deal } from "@/api/types"

@Component({
    components: {
        Bidding,
        CallPanel,
    }
})
export default class BridgeTable extends Vue {
    @Prop() private readonly gameUuid!: string;
    private deal: Deal = {
        calls: [],
    };
    private self = {};

    private async fetchGameState() {
        if (this.gameUuid) {
            const api = this.$store.state.api;
            this.deal = await api.getDeal(this.gameUuid);
            this.self = await api.getSelf(this.gameUuid);
        }
    }

    async mounted() {
        await this.fetchGameState();
        setInterval(this.fetchGameState, 5000);
    }

    @Watch("gameUuid")
    async fetchGameStateOnNewGame() {
        await this.fetchGameState();
    }
}
</script>
