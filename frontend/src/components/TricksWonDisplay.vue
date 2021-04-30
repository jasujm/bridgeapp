<template>
  <div class="tricks-won">
    <ul>
      <li class="us" :class="ourPositions">
        <strong>{{ usText }}:</strong>
        <span class="tricks">{{ ourTricks }}</span>
      </li>
      <li class="them" :class="theirPositions">
        <strong>{{ themText }}:</strong>
        <span class="tricks">{{ theirTricks }}</span>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import Component, { mixins } from "vue-class-component";
import { Prop } from "vue-property-decorator";
import { Position, Trick, Partnership } from "@/api/types";
import SelfPositionMixin from "./selfposition";
import PartnershipMixin from "./partnership";
import _ from "lodash";

@Component
export default class TricksWonDisplay extends mixins(
  SelfPositionMixin,
  PartnershipMixin
) {
  @Prop({ default: () => [] }) private readonly tricks!: Array<Trick>;

  private get usText() {
    return this.selfPosition
      ? "Us"
      : this.partnershipText(Partnership.northSouth);
  }

  private get themText() {
    return this.selfPosition
      ? "Them"
      : this.partnershipText(Partnership.eastWest);
  }

  private get ourPositions() {
    return [this.playerPosition, this.partnerPosition];
  }

  private get theirPositions() {
    return [this.lhoPosition, this.rhoPosition];
  }

  private tricksWon(positions: Array<Position | undefined>) {
    return _.sumBy(this.tricks, (trick) =>
      Number(positions.includes(trick.winner))
    );
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
