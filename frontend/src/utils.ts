import { Position, Partnership } from "./api/types";
import _ from "lodash";

const positionPartnershipMap = {
  north: Partnership.northSouth,
  east: Partnership.eastWest,
  south: Partnership.northSouth,
  west: Partnership.eastWest,
};

export function clockwise(position: Position, n: number) {
  const positions = _.values(Position);
  const m = positions.indexOf(position);
  return positions[(m + n) % positions.length];
}

export function partnerFor(position: Position) {
  return clockwise(position, 2);
}

export function partnershipFor(position: Position) {
  return positionPartnershipMap[position];
}
