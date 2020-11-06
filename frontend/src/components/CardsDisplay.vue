<template>
<div class="cards-display">
    <b-container>
        <b-row>
            <b-col lg="4" offset-lg="4">
                <HandDisplay
                    label="Partner"
                    :cards="cardsFor(partnerPosition)"
                    class="partner"
                    :class="partnerPosition" />
            </b-col>
        </b-row>
        <b-row>
            <b-col lg="4">
                <HandDisplay
                    label="LHO"
                    :cards="cardsFor(lhoPosition)"
                    class="lho"
                    :class="lhoPosition" />
            </b-col>
            <b-col lg="4">
                <TrickDisplay v-if="trick" :trick="trick" />
            </b-col>
            <b-col lg="4">
                <HandDisplay
                    label="RHO"
                    :cards="cardsFor(rhoPosition)"
                    class="rho"
                    :class="rhoPosition" />
            </b-col>
        </b-row>
        <b-row>
            <b-col lg="4" offset-lg="4">
                <HandDisplay
                    label="Self"
                    :cards="cardsFor(selfPosition)"
                    class="self"
                    :class="selfPosition" />
            </b-col>
        </b-row>
    </b-container>
</div>
</template>

<script lang="ts">
import Component, { mixins } from 'vue-class-component'
import { Prop } from "vue-property-decorator"
import HandDisplay from "./HandDisplay.vue"
import TrickDisplay from "./TrickDisplay.vue"
import { Position, Cards, Trick } from "@/api/types"
import SelfPositionMixin from "./selfposition"

@Component({
    components: {
        HandDisplay,
        TrickDisplay,
    }
})
export default class CardsDisplay extends mixins(SelfPositionMixin) {
    @Prop({ default: () => new Cards() }) private readonly cards!: Cards;
    @Prop() private readonly trick?: Trick;

    private cardsFor(position: Position) {
        return this.cards[position];
    }
}
</script>
