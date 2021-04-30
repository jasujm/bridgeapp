import { Vue, Component } from "vue-property-decorator";
import { Position } from "@/api/types";

const positionTexts: Record<Position, string> = {
  north: "North",
  east: "East",
  south: "South",
  west: "West",
};

const positionAbbrevs: Record<Position, string> = {
  north: "N",
  east: "E",
  south: "S",
  west: "W",
};

export function positionText(position: Position) {
  return positionTexts[position];
}

export function positionAbbrev(position: Position) {
  return positionAbbrevs[position];
}

@Component
export default class PositionMixin extends Vue {
  protected positionText(position: Position) {
    return positionText(position);
  }
  protected positionAbbrev(position: Position) {
    return positionAbbrev(position);
  }
}
