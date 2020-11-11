<template>
<span v-html="suitText" class="suit" :class="suit"></span>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator"
import { Suit } from "@/api/types"

@Component
export default class SuitDisplay extends Vue {
    @Prop() private readonly suit!: Suit;

    private get suitText() {
        switch (this.suit) {
            case Suit.clubs:
                return "&clubs;";
            case Suit.diamonds:
                return "&diams;";
            case Suit.hearts:
                return "&hearts;";
            case Suit.spades:
                return "&spades;";
        }
        return "";
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
