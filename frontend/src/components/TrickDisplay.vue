<template>
  <div class="trick">
    <div class="partner">
      <CardDisplay
        v-if="partnerPosition in cards"
        :rank="cards[partnerPosition].rank"
        :suit="cards[partnerPosition].suit"
      />
    </div>
    <div class="opponents">
      <div class="lho">
        <CardDisplay
          v-if="lhoPosition in cards"
          :rank="cards[lhoPosition].rank"
          :suit="cards[lhoPosition].suit"
        />
      </div>
      <div class="rho">
        <CardDisplay
          v-if="rhoPosition in cards"
          :rank="cards[rhoPosition].rank"
          :suit="cards[rhoPosition].suit"
        />
      </div>
    </div>
    <div class="self">
      <CardDisplay
        v-if="playerPosition in cards"
        :rank="cards[playerPosition].rank"
        :suit="cards[playerPosition].suit"
      />
    </div>
  </div>
</template>

<script lang="ts">
import Component, { mixins } from "vue-class-component";
import { Prop } from "vue-property-decorator";
import CardDisplay from "./CardDisplay.vue";
import { Trick } from "@/api/types";
import SelfPositionMixin from "./selfposition";
import _ from "lodash";

@Component({
  components: {
    CardDisplay,
  },
})
export default class TrickDisplay extends mixins(SelfPositionMixin) {
  @Prop({ default: () => ({ cards: [] }) }) private readonly trick!: Trick;

  private get cards() {
    if (this.trick.cards) {
      return _.fromPairs(this.trick.cards.map((pc) => [pc.position, pc.card]));
    }
    return {};
  }
}
</script>

<style lang="scss" scoped>
.trick {
  display: flex;
  flex-direction: column;

  .self,
  .partner {
    display: flex;
    justify-content: center;
    min-height: 1rem;
  }

  .opponents {
    display: flex;
    flex-grow: 10;
    align-items: center;
    justify-content: space-between;
  }
}
</style>
