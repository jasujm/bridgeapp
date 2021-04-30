<template>
  <svg class="card-display" :class="cardClasses" @mousedown="playCard">
    <rect x="0" y="0" rx="4" ry="4" width="100%" height="100%" />
    <text x="4" y="35%" :class="suit">{{ rankText }}</text>
    <text x="4" y="70%" :class="suit" v-html="suitText"></text>
  </svg>
</template>

<script lang="ts">
import Component, { mixins } from "vue-class-component";
import { Prop } from "vue-property-decorator";
import RankDisplayMixin from "./rankdisplaymixin";
import SuitDisplayMixin from "./suitdisplaymixin";

@Component
export default class CardDisplay extends mixins(
  RankDisplayMixin,
  SuitDisplayMixin
) {
  @Prop({ default: () => false }) private readonly allowed!: boolean;

  private get cardClasses() {
    const classes = [`rank-${this.rank}`, `suit-${this.suit}`];
    if (this.allowed) {
      classes.push("allowed");
    }
    return classes;
  }

  private playCard() {
    if (this.allowed) {
      const card = { rank: this.rank, suit: this.suit };
      this.$emit("play", card);
    }
  }
}
</script>

<style lang="scss" scoped>
@import "../styles/mixins";

.card-display {
  cursor: default;
  height: $card-height;
  width: 0.72 * $card-height;
  font: bold 0.45 * $card-height sans-serif;

  rect {
    fill: $body-bg;
    stroke: $dark;
    stroke-width: 2;
  }

  text {
    &.diamonds,
    &.hearts {
      fill: $red-suit-color;
    }
    &.clubs,
    &.spades {
      fill: $black-suit-color;
    }
  }

  &.allowed {
    rect {
      fill: $yellow;
    }
    &:hover {
      margin-top: -1rem;
      margin-bottom: 1rem;
    }
  }
}
</style>
