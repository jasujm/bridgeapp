<template>
<div class="tricks-won">
    <ul>
        <li class="us" :class="ourPositions">
            <strong>Us:</strong> <span class="tricks">{{ ourTricks }}</span>
        </li>
        <li class="them" :class="theirPositions">
            <strong>Them:</strong> <span class="tricks">{{ theirTricks }}</span>
        </li>
    </ul>
</div>
</template>

<script lang="ts">
import Component, { mixins } from 'vue-class-component'
import { Prop } from "vue-property-decorator"
import { Position, Trick } from "@/api/types"
import SelfPositionMixin from "./selfposition"
import { clockwise, partnerFor } from "@/utils"
import _ from "lodash"

@Component
export default class TricksWonDisplay extends mixins(SelfPositionMixin) {
    @Prop({ default: () => [] }) private readonly tricks!: Array<Trick>;

    private get ourPositions() {
        return [this.selfPosition, partnerFor(this.selfPosition)];
    }

    private get theirPositions() {
        return [clockwise(this.selfPosition, 1), clockwise(this.selfPosition, 3)];
    }

    private tricksWon(positions: Array<Position | undefined>) {
        return _.sumBy(
            this.tricks, trick => Number(positions.includes(trick.winner)));
    }

    private get ourTricks() {
        return this.tricksWon(this.ourPositions);
    }

    private get theirTricks() {
        return this.tricksWon(this.theirPositions);
    }
}
</script>

<style lang="scss" scoped>
@import "../styles/mixins";

.tricks-won ul {
  @include bulletless-list;
  @include inline-list;
}
</style>
