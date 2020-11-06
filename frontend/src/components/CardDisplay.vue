<template>
<span class="card-display" :class="cardClasses">{{ rankText(this.rank) }}</span>
</template>

<script lang="ts">
import Component, { mixins } from "vue-class-component"
import { Prop } from "vue-property-decorator"
import { Rank, Suit } from "@/api/types"
import RankDisplayMixin from "./rankdisplay"

@Component
export default class Bidding extends mixins(RankDisplayMixin) {
    @Prop() private readonly rank!: Rank;
    @Prop() private readonly suit!: Suit;

    private get cardClasses() {
        return [`rank-${this.rank}`, `suit-${this.suit}`];
    }
}
</script>

<style lang="scss" scoped>
@import "../styles/suits.scss";

.card-display {
  @include suits;
}
</style>
