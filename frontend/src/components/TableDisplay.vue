<template>
<div class="table-display">
    <b-container>
        <b-row>
            <b-col lg="4" offset-lg="4">
                <HandDisplay
                    :label="handLabel('Partner', partnerPosition)"
                    :cards="cardsFor(partnerPosition)"
                    class="partner"
                    :class="handClasses(partnerPosition)" />
            </b-col>
        </b-row>
        <b-row>
            <b-col lg="4">
                <HandDisplay
                    :label="handLabel('LHO', lhoPosition)"
                    :cards="cardsFor(lhoPosition)"
                    class="lho"
                    :class="handClasses(lhoPosition)" />
            </b-col>
            <b-col lg="4">
                <TrickDisplay v-if="trick" :trick="trick" />
            </b-col>
            <b-col lg="4">
                <HandDisplay
                    :label="handLabel('RHO', rhoPosition)"
                    :cards="cardsFor(rhoPosition)"
                    class="rho"
                    :class="handClasses(rhoPosition)" />
            </b-col>
        </b-row>
        <b-row>
            <b-col lg="4" offset-lg="4">
                <HandDisplay
                    :label="handLabel('Self', selfPosition)"
                    :cards="cardsFor(selfPosition)"
                    class="self"
                    :class="handClasses(selfPosition)" />
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
export default class TableDisplay extends mixins(SelfPositionMixin) {
    @Prop({ default: () => new Cards() }) private readonly cards!: Cards;
    @Prop() private readonly trick?: Trick;
    @Prop() private readonly positionInTurn?: Position;

    private cardsFor(position: Position) {
        return this.cards[position];
    }

    private positionLabel(position: Position) {
        switch (position) {
            case Position.north:
                return "N";
            case Position.east:
                return "E";
            case Position.south:
                return "S";
            case Position.west:
                return "W";
        }
    }

    private handLabel(seat: string, position: Position) {
        return `${seat} (${this.positionLabel(position)})`;
    }

    private handClasses(position: Position) {
        const classes = [position as string];
        if (position == this.positionInTurn) {
            classes.push("turn");
        }
        return classes;
    }
}
</script>
