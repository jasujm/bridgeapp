<template>
  <span class="bid" :class="bidClasses">
    <span class="level">{{ this.bid.level }}</span>
    <span v-if="this.bid.strain == 'notrump'" class="strain notrump">NT</span>
    <SuitDisplay v-else class="strain" :suit="this.bid.strain" />
  </span>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator";
import { Bid } from "@/api/types";
import SuitDisplay from "./SuitDisplay.vue";

@Component({
  components: {
    SuitDisplay,
  },
})
export default class Bidding extends Vue {
  @Prop() private readonly bid!: Bid;

  private get bidClasses() {
    return [`level-${this.bid.level}`, `strain-${this.bid.strain}`];
  }
}
</script>
