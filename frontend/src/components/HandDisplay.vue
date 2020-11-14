<template>
<div class="hand">
    <span class="label">{{ label }}</span>
    <ul>
        <li v-for="group in groupedCards" :key="group.suit">
            <CardListDisplay :suit="group.suit" :ranks="group.ranksInSuit" />
        </li>
    </ul>
</div>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator";
import { Card, Rank, Suit } from "@/api/types"
import _ from "lodash"
import CardListDisplay from "./CardListDisplay.vue"

@Component({
    components: {
        CardListDisplay,
    }
})
export default class HandDisplay extends Vue {
    @Prop() private readonly label!: string;
    @Prop({ default: () => [] }) private readonly cards!: Array<Card | null>;

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
}
</script>

<style lang="scss" scoped>
@import "../styles/mixins";

.hand {
  &.turn .label {
    font-weight: bolder;
  }

  ul {
    @include bulletless-list;
  }

  &.self, &.partner {
    text-align: center;

    ul {
      @include inline-list-down;
    }
  }

  &.lho {
    text-align: right;
  }
}
</style>
