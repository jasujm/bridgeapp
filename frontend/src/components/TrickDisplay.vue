<template>
<div class="trick-display">
    <b-container>
        <b-row>
            <b-col cols="4" offset="4">
                <CardDisplay
                    v-if="partnerPosition in cards"
                    :rank="cards[partnerPosition].rank"
                    :suit="cards[partnerPosition].suit" />
            </b-col>
        </b-row>
        <b-row>
            <b-col cols="4">
                <CardDisplay
                    v-if="lhoPosition in cards"
                    :rank="cards[lhoPosition].rank"
                    :suit="cards[lhoPosition].suit" />
            </b-col>
            <b-col cols="4" offset="4">
                <CardDisplay
                    v-if="rhoPosition in cards"
                    :rank="cards[rhoPosition].rank"
                    :suit="cards[rhoPosition].suit" />
            </b-col>
        </b-row>
        <b-row>
            <b-col cols="4" offset="4">
                <CardDisplay
                    v-if="selfPosition in cards"
                    :rank="cards[selfPosition].rank"
                    :suit="cards[selfPosition].suit" />
            </b-col>
        </b-row>
    </b-container>
</div>
</template>

<script lang="ts">
import Component, { mixins } from 'vue-class-component'
import { Prop } from "vue-property-decorator"
import CardDisplay from "./CardDisplay.vue"
import { Trick } from "@/api/types"
import SelfPositionMixin from "./selfposition"
import _ from "lodash"

@Component({
    components: {
        CardDisplay,
    }
})
export default class TrickDisplay extends mixins(SelfPositionMixin) {
    @Prop({ default: () => ({ cards: [] }) }) private readonly trick!: Trick;

    private get cards() {
        if (this.trick.cards) {
            return _.fromPairs(
                this.trick.cards.map(pc => [pc.position, pc.card])
            );
        }
        return {};
    }
}
</script>

<style lang="scss" scoped>
</style>
