<template>
<span class="call" :class="callClasses">
    {{ callText }}
    <template v-if="this.bid">
        <span v-if="this.bid.strain == 'notrump'" class="notrump">NT</span>
        <SuitDisplay v-else :suit="this.bid.strain" />
    </template>
</span>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator"
import { CallType, Bid } from "@/api/types"
import SuitDisplay from "./SuitDisplay.vue"

@Component({
    components: {
        SuitDisplay
    }
})
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
