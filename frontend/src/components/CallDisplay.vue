<template>
<span class="call" :class="callClasses">{{ callText }}</span>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator"
import { CallType, Bid } from "@/api/types"

@Component
export default class Bidding extends Vue {
    @Prop() private readonly type!: CallType;
    @Prop() private readonly bid?: Bid;

    private get callClasses() {
        let ret: Array<string> = [this.type];
        if (this.bid) {
            ret = ret.concat([`level-${this.bid.level}`, `strain-${this.bid.strain}`]);
        }
        return ret;
    }

    private get callText() {
        switch(this.type) {
            case CallType.pass:
                return "Pass";
            case CallType.double:
                return "X";
            case CallType.redouble:
                return "XX";
            case CallType.bid:
                if (this.bid) {
                    return String(this.bid.level);
                }
        }
        return "";
    }
}
</script>

<style lang="scss" scoped>
@import "../styles/suits.scss";

.call.bid {
  &.strain-clubs::after { @include clubs; }
  &.strain-diamonds::after { @include diamonds; }
  &.strain-hearts::after { @include hearts; }
  &.strain-spades::after { @include spades; }
  &.strain-notrump::after { content: "NT"; }
}
</style>
