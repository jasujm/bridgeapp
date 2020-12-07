<template>
<div class="deal-results">
    <b-table
        class="results"
        :items="items"
        :fields="fields"
        tbody-tr-class="result" />
</div>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator"
import { Partnership, DealResult, DuplicateResult } from "@/api/types"
import { partnershipText } from "./partnership"

function partnershipScore(result: DuplicateResult | null, partnership: Partnership) {
    if (result) {
        if (result.partnership == partnership || result.partnership === null) {
            return String(result.score);
        }
    }
    return "";
}

@Component
export default class DealResultsDisplay extends Vue {
    @Prop() private results!: Array<DealResult>

    private get fields() {
        return [
            {
                key: "northSouthScore",
                label: partnershipText(Partnership.northSouth),
                tdClass: ["score", "north-south"],
            },
            {
                key: "eastWestScore",
                label: partnershipText(Partnership.eastWest),
                tdClass: ["score", "east-west"],
            },
        ]
    }

    private get items() {
        return this.results.map(({ result }) => ({
            northSouthScore: partnershipScore(result, Partnership.northSouth),
            eastWestScore: partnershipScore(result, Partnership.eastWest),
        }));
    }
}
</script>
