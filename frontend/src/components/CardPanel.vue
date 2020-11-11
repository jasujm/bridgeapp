<template>
<div class="card-panel">
    <b-button
        v-for="card in sortedChoices"
        :key="cardKey(card.rank, card.suit)"
        class="m-1"
        variant="outline-dark"
        @click="playCard(card)">
        <CardDisplay :rank="card.rank" :suit="card.suit" />
    </b-button>
</div>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator"
import CardDisplay from "./CardDisplay.vue"
import { Card, Suit, Rank } from "@/api/types"
import _ from "lodash"

function cardKey(rank: Rank, suit: Suit) {
    return `${suit}-${rank}`;
}

const cardCompare = (function() {
    const cardOrderKey: Record<string, number> = {};
    let n = 0;
    for (const suit of _.values(Suit)) {
        for (const rank of _.reverse(_.values(Rank))) {
            cardOrderKey[cardKey(rank, suit)] = n;
            ++n;
        }
    }
    function cardOrder(card: Card) {
        return cardOrderKey[cardKey(card.rank, card.suit)] || -1;
    }
    return function(c1: Card, c2: Card) {
        return cardOrder(c1) - cardOrder(c2);
    }
})();

@Component({
    components: {
        CardDisplay,
    }
})
export default class CardPanel extends Vue {
    @Prop() private readonly gameUuid!: string;
    @Prop({ default: () => [] }) private readonly allowedCards!: Array<Card>;

    private cardKey = cardKey;

    private get sortedChoices() {
        const choices = [...this.allowedCards]
        choices.sort(cardCompare);
        return choices;
    }

    private async playCard(card: Card) {
        if (this.gameUuid) {
            await this.$store.state.api.playCard(this.gameUuid, card);
        }
    }
}
</script>
