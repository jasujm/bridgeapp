<template>
<span class="card-list" :class="'suit-' + suit">
    <SuitDisplay :suit="suit" />
    <span v-for="rank in ranks" :key="rank" class="rank" :class="rankClass(rank)">
        {{ rankText(rank) }}
    </span>
</span>
</template>

<script lang="ts">
import Component, { mixins } from "vue-class-component"
import { Prop } from "vue-property-decorator"
import { Rank, Suit } from "@/api/types"
import SuitDisplay from "./SuitDisplay.vue"
import RankDisplayMixin from "./rankdisplay"

@Component({
    components: {
        SuitDisplay
    }
})
export default class CardDisplay extends mixins(RankDisplayMixin) {
    @Prop() private readonly suit!: Suit;
    @Prop() private readonly ranks!: Rank;
}
</script>
