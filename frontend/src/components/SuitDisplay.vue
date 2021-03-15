<template>
<span v-html="suitText" class="suit" :class="suit"></span>
</template>

<script lang="ts">
import Component, { mixins } from "vue-class-component"
import SuitDisplayMixin from "./suitdisplaymixin"

@Component
export default class SuitDisplay extends mixins(SuitDisplayMixin) {}
</script>

<style lang="scss" scoped>
@import "../styles/mixins";

.suit {
  &.diamonds, &.hearts { color: $red-suit-color; }
  &.clubs, &.spades { color: $black-suit-color; }
}
</style>
