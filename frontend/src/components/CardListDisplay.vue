<template>
<span class="card-list" :class="'suit-' + suit">
    <span v-for="rank in ranks" :key="rank" :class="'rank-' + rank">
        {{ rankText(rank) }}
    </span>
</span>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator";
import { Rank, Suit } from "@/api/types"

@Component
export default class CardDisplay extends Vue {
    @Prop() private readonly suit!: Suit;
    @Prop() private readonly ranks!: Rank;

    private rankText(rank: Rank) {
        switch(rank) {
            case Rank.ace:
                return "A";
            case Rank.king:
                return "K";
            case Rank.queen:
                return "Q";
            case Rank.jack:
                return "J";
        }
        return rank;
    }
}
</script>

<style lang="scss" scoped>
@import "../styles/suits.scss";

.card-list {
  &.suit-clubs::before { @include clubs; }
  &.suit-diamonds::before { @include diamonds; }
  &.suit-hearts::before { @include hearts; }
  &.suit-spades::before { @include spades; }

  .rank {
    padding-left: 0.25rem;
  }
}
</style>
