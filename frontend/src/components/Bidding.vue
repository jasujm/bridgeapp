<template>
<div class="bidding">
    <b-table-simple>
        <b-thead>
            <b-tr>
                <b-th>North</b-th>
                <b-th>East</b-th>
                <b-th>South</b-th>
                <b-th>West</b-th>
            </b-tr>
        </b-thead>
        <b-tbody>
            <b-tr v-for="(callRow, index) in tabulatedCalls" :key="index">
                <b-td v-for="(call, index) in callRow" :key="index">
                    <CallDisplay v-if="call" :type="call.type" :bid="call.bid" />
                </b-td>
            </b-tr>
        </b-tbody>
    </b-table-simple>
</div>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator"
import _ from "lodash"
import CallDisplay from "./CallDisplay.vue"
import { Position, PositionCallPair } from "@/api/types"

@Component({
    components: {
        CallDisplay,
    }
})
export default class Bidding extends Vue {
    @Prop() private readonly calls!: Array<PositionCallPair>;

    private get tabulatedCalls() {
        if (!this.calls || this.calls.length == 0) {
            return [];
        } else {
            const paddingLeft = _.values(Position).indexOf(this.calls[0].position);
            const paddingRight = 3 - (this.calls.length + paddingLeft - 1) % 4;
            const callsWithPadding = _.concat(
                Array(paddingLeft).fill(null),
                this.calls.map(call => call.call),
                Array(paddingRight).fill(null),
            );
            return _.chunk(callsWithPadding, 4);
        }
    }
}
</script>
