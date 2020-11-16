<template>
<span v-html="suitText" class="suit" :class="suit"></span>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator"
import { Suit } from "@/api/types"

const suitTexts = {
    clubs: "&clubs;",
    diamonds: "&diams;",
    hearts: "&hearts;",
    spades: "&spades;",
};

@Component
export default class SuitDisplay extends Vue {
    @Prop() private readonly suit!: Suit;

    private get suitText() {
        return suitTexts[this.suit];
    }
}
</script>

<style lang="scss" scoped>
.suit {
  &.clubs { color: black; }
  &.diamonds { color: red; }
  &.hearts { color: red; }
  &.spades { color: black; }
}
</style>
