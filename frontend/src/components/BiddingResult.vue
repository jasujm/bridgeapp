<template>
<div class="contract-display">
    <PositionDisplay class="declarer" :position="declarer" />
    declares
    <span class="contract">
        <BidDisplay :bid="contract.bid" />
        <span class="doubling" :class="this.contract.doubling">
            {{ doublingText }}
        </span>
    </span>
</div>
</template>

<script lang="ts">
import Component, { mixins } from "vue-class-component"
import { Prop } from "vue-property-decorator"
import { Position, Contract } from "@/api/types"
import SelfPositionMixin from "./selfposition"
import PositionDisplay from "./PositionDisplay.vue"
import BidDisplay from "./BidDisplay.vue"

const doublingTexts = {
    undoubled: "",
    doubled: "X",
    redoubled: "XX",
};

@Component({
    components: {
        PositionDisplay,
        BidDisplay,
    }
})
export default class ContractDisplay extends mixins(SelfPositionMixin) {
    @Prop() private readonly declarer!: Position;
    @Prop() private readonly contract!: Contract;

    private get doublingText() {
        return doublingTexts[this.contract.doubling];
    }
}
</script>

<style lang="scss" scoped>
.declarer, .contract {
  font-weight: bold;
}
</style>
