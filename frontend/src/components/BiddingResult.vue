<template>
<div class="contract-display">
    <strong class="declarer" :class="declarer">{{ declarerText }}</strong>
    declares
    <strong class="contract">
        <BidDisplay :bid="contract.bid" />
        <span class="doubling" :class="this.contract.doubling">
            {{ doublingText }}
        </span>
    </strong>
</div>
</template>

<script lang="ts">
import Component, { mixins } from "vue-class-component"
import { Prop } from "vue-property-decorator"
import { Position, Contract } from "@/api/types"
import SelfPositionMixin from "./selfposition"
import BidDisplay from "./BidDisplay.vue"

const doublingTexts = {
    undoubled: "",
    doubled: "X",
    redoubled: "XX",
};

@Component({
    components: {
        BidDisplay,
    }
})
export default class ContractDisplay extends mixins(SelfPositionMixin) {
    @Prop() private readonly declarer!: Position;
    @Prop() private readonly contract!: Contract;

    private get declarerText() {
        return this.positionText(this.declarer);
    }

    private get doublingText() {
        return doublingTexts[this.contract.doubling];
    }
}
</script>
