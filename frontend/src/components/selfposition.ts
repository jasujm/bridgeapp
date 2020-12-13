import { Component, Prop } from "vue-property-decorator"
import { Position } from "@/api/types"
import { clockwise } from "@/utils"
import PositionMixin from "./position"

@Component
export default class SelfPositionMixin extends PositionMixin {
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
}
