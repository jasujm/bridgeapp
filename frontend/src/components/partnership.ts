import { Vue, Component } from "vue-property-decorator"
import { Partnership } from "@/api/types"

const partnershipTexts = {
    northSouth: "North–South",
    eastWest: "East–West",
}

@Component
export default class PartnershipMixin extends Vue {
    protected partnershipText(partnership: Partnership) {
        return partnershipTexts[partnership];
    }
}
