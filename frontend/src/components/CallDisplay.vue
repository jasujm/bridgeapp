<template>
  <span class="call" :class="callClasses">
    <BidDisplay v-if="bid" :bid="bid" />
    <span v-else :class="type">{{ callText }}</span>
  </span>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator";
import { CallType, Bid } from "@/api/types";
import BidDisplay from "./BidDisplay.vue";

const callTexts = {
  bid: "",
  pass: "Pass",
  double: "X",
  redouble: "XX",
};

@Component({
  components: {
    BidDisplay,
  },
})
export default class Bidding extends Vue {
  @Prop() private readonly type!: CallType;
  @Prop() private readonly bid?: Bid;

  private get callClasses() {
    return [`type-${this.type}`];
  }

  private get callText() {
    return callTexts[this.type];
  }
}
</script>
