<template>
<div class="bridge-table">
    <b-form-group>
        <b-dropdown
            v-if="me.position === null"
            class="join-game any"
            block right split
            variant="primary"
            text="Join table"
            @click="joinGame()">
            <b-dropdown-item
                v-for="position of availablePositions"
                class="join-game"
                :class="position"
                :key="position"
                @click="joinGame(position)">{{ positionText(position) }}</b-dropdown-item>
        </b-dropdown>
        <b-button
            v-else
            class="leave-game"
            block
            variant="secondary"
            @click="leaveGame()">Leave table</b-button>
    </b-form-group>
    <b-container>
        <b-row>
            <b-col lg="4" class="border-bottom mb-4">
                <h3>Results</h3>
                <DealResultsDisplay :results="results" />
                <h3>Bidding</h3>
                <Bidding
                    :northSouthVulnerable="deal.vulnerability.northSouth"
                    :eastWestVulnerable="deal.vulnerability.eastWest"
                    :positionInTurn="deal.positionInTurn"
                    :calls="deal.calls" />
                <BiddingResult
                    v-if="deal.declarer && deal.contract"
                    :selfPosition="me.position"
                    :declarer="deal.declarer"
                    :contract="deal.contract" />
                <TricksWonDisplay
                    v-if="deal.declarer && deal.contract"
                    :selfPosition="me.position"
                    :tricks="deal.tricks" />
            </b-col>
            <b-col lg="8" class="mb-4">
                <h3 class="d-none">Table</h3>
                <TableDisplay
                    :players="players"
                    :selfPosition="me.position"
                    :positionInTurn="deal.positionInTurn"
                    :declarer="deal.declarer"
                    :cards="deal.cards"
                    :trick="displayTrick"
                    :allowedCards="me.allowedCards"
                    @play="playCard($event)" />
            </b-col>
        </b-row>
        <CallPanel :allowedCalls="me.allowedCalls" @call="makeCall($event)" />
    </b-container>
</div>
</template>

<script lang="ts">
import Component, { mixins } from "vue-class-component"
import { Prop, Watch } from "vue-property-decorator"
import { AxiosError } from "axios"
import Bidding from "./Bidding.vue"
import BiddingResult from "./BiddingResult.vue"
import TricksWonDisplay from "./TricksWonDisplay.vue"
import TableDisplay from "./TableDisplay.vue"
import CallPanel from "./CallPanel.vue"
import DealResultsDisplay from "./DealResultsDisplay.vue"
import { partnershipText } from "./partnership"
import PositionMixin from "./position"
import {
    GameCounterPair,
    Deal,
    PlayerState,
    AnyEvent,
    PlayerEvent,
    TurnEvent,
    CallEvent,
    BiddingEvent,
    PlayEvent,
    DummyEvent,
    TrickEvent,
    DealEndEvent,
    Position,
    Trick,
    Call,
    Card,
    DealResult,
    PlayersInGame,
} from "@/api/types"
import { partnershipFor } from "@/utils.ts"
import _ from "lodash"

interface EventCallback {
    counter: number;
    callback: () => void;
}

function scoreMessage({contract, tricksWon, result}: DealEndEvent, position: Position | null) {
    if (contract && tricksWon && result.partnership) {
        const resultMessage = `Declarer made ${tricksWon} tricks.`;
        const contractMadeMessage = `Contract ${tricksWon >= contract.bid.level + 6 ? "made" : "defeated"}.`
        let scoreMessage = "";
        if (position) {
            const who = partnershipFor(position) == result.partnership ?
                "You score" : "Opponent scores";
            scoreMessage = `${who} ${result.score} points`;
        } else {
            scoreMessage = `${partnershipText(result.partnership)} scores ${result.score} points`;
        }
        return `${resultMessage}\n${contractMadeMessage}\n${scoreMessage}`;
    } else {
        return "Passed out";
    }
}

@Component({
    components: {
        Bidding,
        BiddingResult,
        TricksWonDisplay,
        TableDisplay,
        CallPanel,
        DealResultsDisplay,
    }
})
export default class BridgeTable extends mixins(PositionMixin) {
    @Prop() private readonly gameId!: string;
    private deal = new Deal();
    private me = new PlayerState();
    private results: Array<DealResult> = [];
    private players = new PlayersInGame();
    private displayTrick: Trick | null = null;
    private nextDisplayTrick: Trick | null = null;
    private ws?: WebSocket;
    private fetchGameTimerId?: number;
    private displayTrickTimerId?: number;
    private dealCounter: number | null = Number.POSITIVE_INFINITY;
    private eventCounter: number = Number.NEGATIVE_INFINITY;
    private eventCallbacks: Array<EventCallback> = [];

    refresh() {
        this.fetchGameState();
    }

    private fetchDealState() {
        if (this.gameId) {
            const api = this.$store.state.api;
            api.getDeal(this.gameId).then(
                (deal: Deal) => {
                    this.deal = deal || new Deal();
                }
            ).catch((err: Error) => this.$store.dispatch("reportError", err));
        }
    }

    private fetchPlayerState() {
        if (this.gameId) {
            const api = this.$store.state.api;
            api.getPlayerState(this.gameId).then(
                (me: PlayerState) => this.me = me
            ).catch((err: Error) => this.$store.dispatch("reportError", err));
        }
    }

    private fetchGameState() {
        if (this.gameId) {
            const api = this.$store.state.api;
            api.getGame(this.gameId).then(
                ({ game, counter }: GameCounterPair) => {
                    this.deal = game.deal || new Deal();
                    this.me = game.me;
                    this.results = game.results;
                    this.players = game.players;
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
            ).catch((err: Error) => this.$store.dispatch("reportError", err));
        }
    }

    private get availablePositions() {
        return _.values(Position).filter(p => this.players[p] === null);
    }

    private joinGame(position?: Position) {
        if (this.gameId) {
            const api = this.$store.state.api;
            api.joinGame(this.gameId, position).then(
                () => {
                    this.fetchPlayerState();
                    this.fetchDealState();
                }
            ).catch(
                (err: Error) => this.$store.dispatch("reportError", err)
            );
        }
    }

    private leaveGame() {
        if (this.gameId) {
            const api = this.$store.state.api;
            api.leaveGame(this.gameId).then(
                () => {
                    this.me = new PlayerState();
                    this.fetchDealState();
                }
            ).catch(
                (err: Error) => this.$store.dispatch("reportError", err)
            );
        }
    }

    private changePlayer({ position, player }: PlayerEvent) {
        this.players[position] = player;
    }

    private addCall({ position, call, index }: CallEvent) {
        this.$set(this.deal.calls, index, { position, call });
    }

    private completeBidding({ declarer, contract }: BiddingEvent) {
        this.deal.declarer = declarer;
        this.deal.contract = contract;
    }

    private cardPlayed({ position, card, trick: trickIndex, index: cardIndex }: PlayEvent) {
        if (!this.deal.tricks[trickIndex]) {
            this.$set(this.deal.tricks, trickIndex, { cards: [] });
        }
        const trick = this.deal.tricks[trickIndex];
        this.$set(trick.cards, cardIndex, { position, card });
        this.updateDisplayTrick(trick);
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

    private revealDummy({ position, cards }: DummyEvent) {
        this.deal.cards[position] = cards;
    }

    private completeTrick({ winner, index }: TrickEvent) {
        this.deal.tricks[index].winner = winner;
        this.updateDisplayTrick(null);
    }

    private recordScore(event: DealEndEvent) {
        const latestResult = _.last(this.results)
        if (latestResult && latestResult.deal == event.deal) {
            latestResult.result = event.result;
        } else {
            this.results.push({ deal: event.deal, result: event.result });
        }
        const message = scoreMessage(event, this.me.position);
        this.$bvToast.toast(message, {
            title: "Deal result",
            autoHideDelay: 5000,
        });
    }

    private handleTurn({ position }: TurnEvent) {
        this.deal.positionInTurn = position;
        if (position == this.me.position) {
            this.fetchPlayerState();
        } else {
            this.me.allowedCalls = [];
            this.me.allowedCards = [];
        }
    }

    private handleConflictError(err: Error) {
        const axiosError = err as AxiosError;
        if (axiosError.isAxiosError && axiosError.response && axiosError.response.status == 409) {
            this.fetchPlayerState();
        } else {
            this.$store.dispatch("reportError", err);
        }
    }

    private makeCall(call: Call) {
        if (this.gameId) {
            this.$store.state.api.makeCall(this.gameId, call).catch(
                this.handleConflictError.bind(this)
            );
        }
    }

    private playCard(card: Card) {
        if (this.gameId) {
            this.$store.state.api.playCard(this.gameId, card).catch(
                this.handleConflictError.bind(this)
            );
        }
    }

    private wrapEventHandler<Event extends AnyEvent>(callback: (event: Event) => void) {
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
    }

    private startGame() {
        this.close();
        this.ws = this.$store.state.api.subscribe(
            this.gameId,
            {
                open: this.fetchGameState.bind(this),
                player: this.wrapEventHandler(this.changePlayer),
                deal: this.fetchGameState.bind(this),
                turn: this.wrapEventHandler(this.handleTurn),
                call: this.wrapEventHandler(this.addCall),
                bidding: this.wrapEventHandler(this.completeBidding),
                play: this.wrapEventHandler(this.cardPlayed),
                dummy: this.wrapEventHandler(this.revealDummy),
                trick: this.wrapEventHandler(this.completeTrick),
                dealend: this.wrapEventHandler(this.recordScore),
            }
        );
        this.fetchGameState();
        this.fetchGameTimerId = setInterval(this.fetchGameState, 10000);
        this.updateDisplayTrick(this.lastTrick);
    }

    private close() {
        if (this.fetchGameTimerId) {
            clearInterval(this.fetchGameTimerId);
        }
        if (this.displayTrickTimerId) {
            clearTimeout(this.displayTrickTimerId);
        }
        if (this.ws) {
            this.ws.close();
        }
    }

    beforeDestroy() {
        this.close();
    }

    @Watch("gameId")
    private gameIdChanged() {
        if (this.$store.getters.isLoggedIn) {
            this.startGame();
        }
    }

    @Watch("$store.getters.isLoggedIn", { immediate: true })
    private loggedIn(value: boolean) {
        if (value) {
            this.startGame();
        }
    }

    private get lastTrick() {
        return _.last(this.deal.tricks) || null;
    }

    private canReplaceDisplayTrick(trick: Trick | null) {
        if (!this.displayTrick) {
            return true;
        }
        if (!trick) {
            return false;
        }
        const prefixLength = this.displayTrick.cards.length;
        return _.isEqual(trick.cards.slice(0, prefixLength), this.displayTrick.cards.slice(0, prefixLength));
    }

    private updateDisplayTrick(trick: Trick | null) {
        if (this.canReplaceDisplayTrick(trick)) {
            this.displayTrick = trick;
        } else {
            this.nextDisplayTrick = trick;
            if (this.displayTrickTimerId === undefined) {
                this.displayTrickTimerId = setTimeout(
                    () => {
                        this.displayTrick = this.nextDisplayTrick;
                        this.nextDisplayTrick = null;
                        this.displayTrickTimerId = undefined;
                    }, 2000
                );
            }
        }
    }

    @Watch("deal.tricks")
    private trickChanged() {
        this.updateDisplayTrick(this.lastTrick);
    }
}
</script>

<style lang="scss" scoped>
@import "~bootstrap/scss/functions";
@import "~bootstrap/scss/variables";

.bidding, .deal-results {
  height: 10rem;
  overflow-y: scroll;
  margin-bottom: $spacer;
}

::v-deep .turn::before {
  content: "\25B8";
  padding-right: 0.25*$spacer;
}
</style>
