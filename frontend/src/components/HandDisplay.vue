<template>
<div class="hand">
    <ul class="suits">
        <li v-for="group in groupedCards" :key="group.suit">
            <ul class="cards" :class="'suit-' + group.suit">
                <li v-for="rank in group.ranksInSuit" :key="rank">
                    <CardDisplay :rank="rank" :suit="group.suit" @play="$emit('play', $event)" :allowed="isAllowed(rank, group.suit)" />
                </li>
            </ul>
        </li>
    </ul>
</div>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator";
import { Card, Rank, Suit } from "@/api/types"
import CardDisplay from "./CardDisplay.vue"
import _ from "lodash"

@Component({
    components: {
        CardDisplay
    }
})
export default class HandDisplay extends Vue {
    @Prop({ default: () => [] }) private readonly cards!: Array<Card | null>;
    @Prop({ default: () => [] }) private readonly allowedCards!: Array<Card>;

    private get groupedCards() {
        // This might not be an optimal performer due to repeatedly doing
        // indexOf() to sort suits and ranks. But then again the arrays are
        // small...
        const cards = _.groupBy(_.compact(this.cards), card => card.suit);
        const cards2 = [];
        const suits = _.values(Suit) as Array<string>;
        const ranks = _.values(Rank) as Array<string>;
        const suitsInGroups = _.keys(cards);
        suitsInGroups.sort((a, b) => suits.indexOf(a) - suits.indexOf(b));
        for (const suit of suitsInGroups) {
            const ranksInSuit = cards[suit].map(card => card.rank);
            ranksInSuit.sort((a, b) => ranks.indexOf(b) - ranks.indexOf(a));
            cards2.push({
                suit,
                ranksInSuit,
            });
        }
        return cards2;
    }

    private isAllowed(rank: Rank, suit: Suit) {
        return this.allowedCards.some(
            card => card.rank == rank && card.suit == suit
        );
    }
}
</script>

<style lang="scss" scoped>
@import "../styles/mixins";

.hand {
  margin-left: $card-overlap;
  ::v-deep .card-display {
    margin-left: -$card-overlap;
  }
  ul.suits {
    @include bulletless-list;

    ul.cards {
      @include bulletless-list;
      @include inline-list($margin: false);
      display: inline;
    }
  }
}
</style>
