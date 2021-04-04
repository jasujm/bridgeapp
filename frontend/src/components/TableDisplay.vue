<template>
<div class="table-display">
    <b-row>
        <b-col md="12">
            <div class="seat partner" :class="handClasses(partnerPosition)">
                <SeatLabel
                    :player="players[partnerPosition]"
                    :position="partnerPosition" />
                <HandDisplay
                    :cards="cardsFor(partnerPosition)"
                    :allowedCards="allowedCards"
                    @play="$emit('play', $event)" />
            </div>
        </b-col>
    </b-row>
    <b-row>
        <b-col cols="4">
            <div class="seat lho" :class="handClasses(lhoPosition)">
                <SeatLabel
                    :player="players[lhoPosition]"
                    :position="lhoPosition" />
                <HandDisplay :cards="cardsFor(lhoPosition)" />
            </div>
        </b-col>
        <b-col id="trick-display-col" cols="4">
            <TrickDisplay
                v-if="trick"
                :player="players[selfPosition]"
                :trick="trick"
                :selfPosition="selfPosition" />
        </b-col>
        <b-col cols="4">
            <div class="seat rho" :class="handClasses(rhoPosition)">
                <SeatLabel
                    :player="players[rhoPosition]"
                    :position="rhoPosition" />
                <HandDisplay :cards="cardsFor(rhoPosition)" />
            </div>
        </b-col>
    </b-row>
    <b-row>
        <b-col md="12">
            <div class="seat self" :class="handClasses(playerPosition)">
                <SeatLabel
                    :player="players[playerPosition]"
                    :position="playerPosition" />
                <HandDisplay
                    :cards="cardsFor(playerPosition)"
                    :allowedCards="allowedCards"
                    @play="$emit('play', $event)" />
            </div>
        </b-col>
    </b-row>
</div>
</template>

<script lang="ts">
import Component, { mixins } from "vue-class-component"
import { Prop } from "vue-property-decorator"
import SeatLabel from "./SeatLabel.vue"
import HandDisplay from "./HandDisplay.vue"
import TrickDisplay from "./TrickDisplay.vue"
import { PlayersInGame, Position, Cards, Trick, Card } from "@/api/types"
import SelfPositionMixin from "./selfposition"
import { partnerFor } from "@/utils"

@Component({
    components: {
        SeatLabel,
        HandDisplay,
        TrickDisplay,
    }
})
export default class TableDisplay extends mixins(SelfPositionMixin) {
    @Prop({ default: () => new PlayersInGame() }) private readonly players!: PlayersInGame;
    @Prop({ default: () => new Cards() }) private readonly cards!: Cards;
    @Prop({ default: () => [] }) allowedCards!: Array<Card>;
    @Prop() private readonly trick?: Trick;
    @Prop() private readonly positionInTurn?: Position;
    @Prop() private readonly declarer?: Position;

    private cardsFor(position: Position) {
        return this.cards[position];
    }

    private handClasses(position: Position) {
        const classes = [position as string];
        if (position == this.positionInTurn) {
            classes.push("turn");
        }
        if (position == this.declarer) {
            classes.push("declarer");
        } else if (partnerFor(position) == this.declarer) {
            classes.push("dummy");
        }
        return classes;
    }
}
</script>

<style lang="scss" scoped>
@import "~bootstrap/scss/functions";
@import "~bootstrap/scss/variables";
@import "~bootstrap/scss/mixins";
@import "../styles/mixins";

#trick-display-col {
  background-color: #f2ffe6;
  border: 1px solid #479900;
  padding: 10px;
  height: 4*$card-height + 1rem;

  .trick {
    height: 100%;
  }
}

.seat {
  &.self, &.partner {
    text-align: center;

    ::v-deep ul {
      @include inline-list;
    }
  }

  &.lho {
    text-align: right;
  }
}
</style>
