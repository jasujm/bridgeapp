<template>
<div class="bridge-table">
    <b-container>
        <b-row>
            <b-col lg="4">
                <Bidding :calls="deal.calls" />
            </b-col>
            <b-col lg="8">
                <TableDisplay
                    :selfPosition="self.position"
                    :cards="deal.cards"
                    :trick="deal.tricks[deal.tricks.length - 1]" />
            </b-col>
        </b-row>
        <CallPanel :gameUuid="gameUuid" :allowedCalls="self.allowedCalls" />
        <CardPanel :gameUuid="gameUuid" :allowedCards="self.allowedCards" />
    </b-container>
</div>
</template>

<script lang="ts">
import { Vue, Component, Prop, Watch } from "vue-property-decorator"
import Bidding from "./Bidding.vue"
import TableDisplay from "./TableDisplay.vue"
import CallPanel from "./CallPanel.vue"
import CardPanel from "./CardPanel.vue"
import { Deal, Self } from "@/api/types"

@Component({
    components: {
        Bidding,
        TableDisplay,
        CallPanel,
        CardPanel,
    }
})
export default class BridgeTable extends Vue {
    @Prop() private readonly gameUuid!: string;
    private deal = new Deal();
    private self = new Self();

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
