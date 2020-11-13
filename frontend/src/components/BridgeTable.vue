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
                    :declarer="deal.declarer"
                    :cards="deal.cards"
                    :trick="displayTrick" />
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
    Deal,
    Self,
    TurnEvent,
    CallEvent,
    BiddingEvent,
    PlayEvent,
    DummyEvent,
    DealEndEvent,
    Score,
    Position,
    Partnership,
    Trick,
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
    private displayTrick: Trick = {};
    private ws?: WebSocket;
    private timerId!: number;

    private async fetchDealState() {
        if (this.gameUuid) {
            const api = this.$store.state.api;
            this.deal = await api.getDeal(this.gameUuid);
        }
    }

    private async fetchSelfState() {
        if (this.gameUuid) {
            const api = this.$store.state.api;
            this.self = await api.getSelf(this.gameUuid);
        }
    }

    private async fetchGameState() {
        await Promise.all([this.fetchDealState(), this.fetchSelfState()]);
    }

    private addCall({ position, call }: CallEvent) {
        this.deal.calls.push({ position, call });
    }

    private completeBidding({ declarer }: BiddingEvent) {
        this.deal.declarer = declarer;
    }

    private playCard({ position, card }: PlayEvent) {
        const trick = _.last(this.deal.tricks)
        if (trick && trick.cards) {
            trick.cards.push({ position, card });
            const hand = this.deal.cards[position];
            let index = _.findIndex(
                hand,
                c => c ? c.rank == card.rank && c.suit == card.suit : false
            );
            // If the cards are unknown, just remove one of the unknowns
            if (index < 0) {
                index = hand.indexOf(null);
            }
            if (index >= 0) {
                hand.splice(index, 1);
            }
        }
    }

    private revealDummy({ position, cards }: DummyEvent) {
        this.deal.cards[position] = cards;
    }

    private completeTrick() {
        // TODO: Ideally the event itself would include the information if this
        // is the last trick. But needs API support.
        if (this.deal.tricks.length < 13) {
            this.deal.tricks.push({ cards: [] });
        }
    }

    private recordScore({ score }: DealEndEvent) {
        // TODO: Ideally, there would be a scoresheet component listing deal
        // history and scores. But needs API support for retrieving past deal
        // results.
        const message = (function(score: Score | null, position: Position) {
            const partnershipOf = {
                north: Partnership.northSouth,
                east: Partnership.eastWest,
                south: Partnership.northSouth,
                west: Partnership.eastWest,
            };
            if (score) {
                const who = (partnershipOf[position] as Partnership) == score.partnership ?
                    "You score" : "Opponent scores";
                return `${who} ${score.score} points`;
            } else {
                return "Passed out";
            }
        })(score, this.self.position);
        this.$bvToast.toast(message, {
            title: "Deal result",
            autoHideDelay: 5000,
        });
    }

    private async handleTurn({ position }: TurnEvent) {
        this.deal.positionInTurn = position;
        if (position == this.self.position) {
            await this.fetchSelfState();
        } else {
            this.self.allowedCalls = [];
            this.self.allowedCards = [];
        }
    }

    private async startGame() {
        this.ws = this.$store.state.api.subscribe(
            this.gameUuid,
            {
                deal: this.fetchDealState.bind(this),
                turn: this.handleTurn.bind(this),
                call: this.addCall.bind(this),
                bidding: this.completeBidding.bind(this),
                play: this.playCard.bind(this),
                dummy: this.revealDummy.bind(this),
                trick: this.completeTrick.bind(this),
                dealend: this.recordScore.bind(this),
            }
        );
        await this.fetchGameState();
        this.timerId = setInterval(this.fetchGameState, 10000);
    }

    private close() {
        clearInterval(this.timerId);
        if (this.ws) {
            this.ws.close();
        }
    }

    async mounted() {
        await this.startGame();
        this.displayTrick = this.lastTrick;
    }

    beforeDestroy() {
        this.close();
    }

    @Watch("gameUuid")
    private async gameUuidChanged() {
        this.close();
        await this.startGame();
    }

    private get lastTrick() {
        return _.last(this.deal.tricks) || {};
    }

    @Watch("lastTrick")
    private async trickChanged() {
        // This visually retains the old trick for two seconds after new trick
        // is started
        const trick = this.lastTrick;
        const delay = _.isEmpty(trick.cards) ? 2000 : 0;
        _.delay(() => this.displayTrick = trick, delay);
    }
}
</script>
