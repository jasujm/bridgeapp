<template>
<div class="bridge-table">
    <b-container>
        <b-row>
            <b-col lg="4">
                <Bidding
                    :northSouthVulnerable="deal.vulnerability.northSouth"
                    :eastWestVulnerable="deal.vulnerability.eastWest"
                    :calls="deal.calls" />
            </b-col>
            <b-col lg="8">
                <TableDisplay
                    :selfPosition="self.position"
                    :positionInTurn="deal.positionInTurn"
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
import _ from "lodash"

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
    private ws?: WebSocket;
    private timerId!: number;

    private fetchGameState = _.debounce(this._fetchGameState, 50);

    private async _fetchGameState() {
        if (this.gameUuid) {
            const api = this.$store.state.api;
            this.deal = await api.getDeal(this.gameUuid);
            this.self = await api.getSelf(this.gameUuid);
        }
    }

    private async _onNewGame() {
        // TODO: Ideally a more fine-grained subscribe callback to only update
        // what is needed
        this.ws = this.$store.state.api.subscribe(this.gameUuid, this.fetchGameState);
        await this.fetchGameState();
        this.timerId = setInterval(this.fetchGameState, 5000);
    }

    private close() {
        clearTimeout(this.timerId);
        this.fetchGameState.cancel();
        if (this.ws) {
            this.ws.close();
        }
    }

    async mounted() {
        await this._onNewGame();
    }

    beforeDestroy() {
        this.close();
    }

    @Watch("gameUuid")
    private async onNewGame() {
        this.close();
        await this._onNewGame();
    }
}
</script>
