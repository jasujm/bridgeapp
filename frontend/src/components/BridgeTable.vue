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
import {
    Deal, Self, Event, DealEndEvent, Score, EventCallback, Position, Partnership
} from "@/api/types"
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
    private eventHandlers!: Record<string, EventCallback>;
    private ws?: WebSocket;
    private timerId!: number;

    async fetchGameStateImpl() {
        if (this.gameUuid) {
            const api = this.$store.state.api;
            [this.deal, this.self] = await Promise.all(
                [api.getDeal(this.gameUuid), api.getSelf(this.gameUuid)]
            );
        }
    }
    private fetchGameState = _.debounce(this.fetchGameStateImpl, 50);

    recordScore(event: DealEndEvent) {
        // TODO: Ideally, there would be a scoresheet component listing deal
        // history and scores. But needs API support for retrieving past deal
        // results.
        const message = (function(score: Score | null, position: Position) {
            const partnershipOf = {
                [Position.north]: Partnership.northSouth,
                [Position.east]: Partnership.eastWest,
                [Position.south]: Partnership.northSouth,
                [Position.west]: Partnership.eastWest,
            };
            if (score) {
                const who = (partnershipOf[position] as Partnership) == score.partnership ?
                    "You score" : "Opponent scores";
                return `${who} ${score.score} points`;
            } else {
                return "Passed out";
            }
        })(event.score, this.self.position);
        this.$bvToast.toast(message, {
            title: "Deal result",
            autoHideDelay: 5000,
        });
    }

    private handleEvent(event: Event) {
        const handler = this.eventHandlers[event.type] ||
            this.eventHandlers.default;
        handler.call(this, event);
    }

    private async startGame() {
        // TODO: Ideally a more fine-grained subscribe callback to only update
        // what is needed
        this.ws = this.$store.state.api.subscribe(this.gameUuid, this.handleEvent);
        await this.fetchGameState();
        this.timerId = setInterval(this.fetchGameState, 5000);
    }

    private close() {
        clearInterval(this.timerId);
        this.fetchGameState.cancel();
        if (this.ws) {
            this.ws.close();
        }
    }

    created() {
        this.eventHandlers = {
            default: this.fetchGameState,
            dealend: this.recordScore as EventCallback,
        }
    }

    async mounted() {
        await this.startGame();
    }

    beforeDestroy() {
        this.close();
    }

    @Watch("gameUuid")
    private async gameUuidChanged() {
        this.close();
        await this.startGame();
    }
}
</script>
