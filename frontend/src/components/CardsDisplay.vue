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
            <b-col lg="4" offset-lg="4">
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
                    :cards="cardsFor(position)"
                    class="self"
                    :class="position" />
            </b-col>
        </b-row>
    </b-container>
</div>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator"
import _ from "lodash"
import HandDisplay from "./HandDisplay.vue"
import { Position, Cards } from "@/api/types"

@Component({
    components: {
        HandDisplay,
    }
})
export default class CardsDisplay extends Vue {
    @Prop({ default: Position.north }) private readonly position!: Position;
    @Prop({ default: new Cards() }) private readonly cards!: Cards;

    private cardsFor(position: Position) {
        return this.cards[position];
    }

    private clockwise(n: number) {
        const positions = _.values(Position);
        const m = positions.indexOf(this.position);
        return positions[(m + n) % positions.length];
    }

    private get lhoPosition() {
        return this.clockwise(1);
    }

    private get partnerPosition() {
        return this.clockwise(2);
    }

    private get rhoPosition() {
        return this.clockwise(3);
    }
}
</script>
