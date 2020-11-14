import { Position } from "./api/types"
import _ from "lodash"

export function clockwise(position: Position, n: number) {
    const positions = _.values(Position);
    const m = positions.indexOf(position);
    return positions[(m + n) % positions.length];
}

export function partnerFor(position: Position) {
    return clockwise(position, 2);
}
