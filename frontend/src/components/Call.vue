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
.call.bid {
    &.strain-clubs:after { content: "\2663"; color: black; }
    &.strain-diamonds:after { content: "\2666"; color: red; }
    &.strain-hearts:after { content: "\2665"; color: red; }
    &.strain-spades:after { content: "\2660"; color: black; }
    &.strain-notrump:after { content: "NT"; }
}
</style>
