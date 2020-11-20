import { Vue, Component, Prop } from "vue-property-decorator"
import { Position } from "@/api/types"
import { clockwise } from "@/utils"

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

@Component
export default class SelfPositionMixin extends Vue {
    @Prop({ default: null }) protected readonly selfPosition!: Position | null;

    protected get joined() {
        return this.selfPosition !== null;
    }

    protected get playerPosition() {
        return this.selfPosition || Position.south;
    }

    protected get lhoPosition() {
        return clockwise(this.playerPosition, 1);
    }

    protected get partnerPosition() {
        return clockwise(this.playerPosition, 2);
    }

    protected get rhoPosition() {
        return clockwise(this.playerPosition, 3);
    }

    protected positionText(position: Position) {
        return positionTexts[position];
    }

    protected positionAbbrev(position: Position) {
        return positionAbbrevs[position];
    }
}
