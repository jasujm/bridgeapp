import { Vue, Component } from "vue-property-decorator";
import { Partnership } from "@/api/types";

const partnershipTexts = {
  northSouth: "North–South",
  eastWest: "East–West",
};

export function partnershipText(partnership: Partnership) {
  return partnershipTexts[partnership];
}

@Component
export default class PartnershipMixin extends Vue {
  protected partnershipText(partnership: Partnership) {
    return partnershipText(partnership);
  }
}
