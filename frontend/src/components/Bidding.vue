<template>
<div class="bidding">
    <table class="table">
        <thead>
            <tr>
                <th>North</th>
                <th>East</th>
                <th>South</th>
                <th>West</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="callRow in tabulatedCalls">
                <td v-for="call in callRow">
                    <Call v-if="call" :type="call.type" :bid="call.bid" />
                </td>
            </tr>
        </tbody>
    </table>
</div>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator"
import _ from "lodash"
import {  Position, PositionCallPair } from "@/api/types"
import Call from "./Call.vue"

@Component({
    components: {
        Call,
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
