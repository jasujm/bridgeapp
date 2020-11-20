<template>
<div class="bridge-table">
    <b-alert :show="self.position === null" variant="info">
        You have not joined this game. You can do so with the “Join” button.
    </b-alert>
    <b-container>
        <b-row>
            <b-col lg="4">
                <Bidding
                    :northSouthVulnerable="deal.vulnerability.northSouth"
                    :eastWestVulnerable="deal.vulnerability.eastWest"
                    :calls="deal.calls" />
                <BiddingResult
                    v-if="deal.declarer && deal.contract"
                    :selfPosition="self.position"
                    :declarer="deal.declarer"
                    :contract="deal.contract" />
                <TricksWonDisplay
                    v-if="deal.declarer && deal.contract"
                    :selfPosition="self.position"
                    :tricks="deal.tricks" />
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
import BiddingResult from "./BiddingResult.vue"
import TricksWonDisplay from "./TricksWonDisplay.vue"
import TableDisplay from "./TableDisplay.vue"
import CallPanel from "./CallPanel.vue"
import CardPanel from "./CardPanel.vue"
import {
    Deal,
    DealCounterPair,
    Self,
    Event,
    TurnEvent,
    CallEvent,
    BiddingEvent,
    PlayEvent,
    DummyEvent,
    TrickEvent,
    DealEndEvent,
    Score,
    Position,
    Partnership,
    Trick,
} from "@/api/types"
import _ from "lodash"

interface EventCallback {
    counter: number;
    callback: () => void;
}

@Component({
    components: {
        Bidding,
        BiddingResult,
        TricksWonDisplay,
        TableDisplay,
        CallPanel,
        CardPanel,
    }
})
export default class BridgeTable extends Vue {
    @Prop() private readonly gameUuid!: string;
    private deal = new Deal();
    private self = new Self();
    private displayTrick: Trick | null = null;
    private ws?: WebSocket;
    private timerId!: number;
    private dealCounter: number | null = Number.POSITIVE_INFINITY;
    private eventCounter: number = Number.NEGATIVE_INFINITY;
    private eventCallbacks: Array<EventCallback> = [];

    refresh() {
        this.fetchGameState();
    }

    private _fetchDealState() {
        if (this.gameUuid) {
            const api = this.$store.state.api;
            api.getDeal(this.gameUuid).then(
                ({ deal, counter }: DealCounterPair) => {
                    this.deal = deal || new Deal();
                    this.dealCounter = counter;
                    // Apply the queued events whose counter value is higher than the
                    // current counter value
                    for (const cb of this.eventCallbacks) {
                        if (counter && cb.counter > counter) {
                            cb.callback();
                        }
                    }
                    this.eventCallbacks.splice(0, this.eventCallbacks.length);
                }
            );
        }
    }

    private fetchDealState = _.debounce(this._fetchDealState, 50, { trailing: true })

    private _fetchSelfState() {
        if (this.gameUuid) {
            const api = this.$store.state.api;
            api.getSelf(this.gameUuid).then((self: Self) => this.self = self);
        }
    }

    private fetchSelfState = _.debounce(this._fetchSelfState, 50, { trailing: true })

    private fetchGameState() {
        this.fetchDealState();
        this.fetchSelfState();
    }

    private addCall({ position, call }: CallEvent) {
        this.deal.calls.push({ position, call });
    }

    private addTrick() {
        this.deal.tricks.push({ cards: [] });
    }

    private completeBidding({ declarer, contract }: BiddingEvent) {
        this.deal.declarer = declarer;
        this.deal.contract = contract;
        if (declarer) {
            this.addTrick();
        }
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

    private completeTrick({ winner }: TrickEvent) {
        // TODO: Ideally the event itself would include the information if this
        // is the last trick. But needs API support.
        const lastTrick = _.last(this.deal.tricks);
        if (lastTrick) {
            lastTrick.winner = winner;
        }
        if (this.deal.tricks.length < 13) {
            this.addTrick();
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

    private handleTurn({ position }: TurnEvent) {
        this.deal.positionInTurn = position;
        if (position == this.self.position) {
            this.fetchSelfState();
        } else {
            this.self.allowedCalls = [];
            this.self.allowedCards = [];
        }
    }

    private startGame() {
        const wrap = (callback: (event: Event) => void) => {
            return (event: Event) => {
                if (event.counter > this.eventCounter) {
                    // Queue events if their counter is not larger than the biggest
                    // known deal counter
                    this.eventCounter = event.counter;
                    const invokeCallback = () => callback.call(this, event);
                    if (this.dealCounter === null || event.counter > this.dealCounter) {
                        invokeCallback();
                    } else if (this.dealCounter >= event.counter) {
                        this.eventCallbacks.push({
                            counter: event.counter,
                            callback: invokeCallback,
                        });
                    }
                } else {
                    // Event counter wrapped, refresh state and start over
                    this.dealCounter = Number.POSITIVE_INFINITY;
                    this.eventCounter = Number.NEGATIVE_INFINITY;
                    this.fetchGameState();
                }
            }
        };
        this.ws = this.$store.state.api.subscribe(
            this.gameUuid,
            {
                open: this.fetchGameState.bind(this),
                deal: wrap(this.fetchDealState),  // @ts-ignore
                turn: wrap(this.handleTurn),  // @ts-ignore
                call: wrap(this.addCall),  // @ts-ignore
                bidding: wrap(this.completeBidding),  // @ts-ignore
                play: wrap(this.playCard),  // @ts-ignore
                dummy: wrap(this.revealDummy),  // @ts-ignore
                trick: wrap(this.completeTrick),  // @ts-ignore
                dealend: wrap(this.recordScore),  // @ts-ignore
            }
        );
        this.fetchGameState();
        this.timerId = setInterval(this.fetchGameState, 10000);
    }

    private close() {
        clearInterval(this.timerId);
        if (this.ws) {
            this.ws.close();
        }
    }

    mounted() {
        this.startGame();
        this.displayTrick = this.lastTrick;
    }

    beforeDestroy() {
        this.close();
    }

    @Watch("gameUuid")
    private gameUuidChanged() {
        this.close();
        this.startGame();
    }

    private get lastTrick() {
        return _.last(this.deal.tricks) || null;
    }

    @Watch("lastTrick")
    private trickChanged() {
        // This visually retains the old trick for two seconds after new trick
        // is started
        const trick = this.lastTrick;
        const delay = (!trick || _.isEmpty(trick.cards)) ? 2000 : 0;
        _.delay(() => this.displayTrick = trick, delay);
    }
}
</script>
