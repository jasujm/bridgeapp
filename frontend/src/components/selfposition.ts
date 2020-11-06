import { Vue, Component, Prop } from "vue-property-decorator"
import { Position } from "@/api/types"
import _ from "lodash"

@Component
export default class SelfPositionMixin extends Vue {
    @Prop({ default: Position.north }) protected readonly selfPosition!: Position;

    protected clockwise(n: number) {
        const positions = _.values(Position);
        const m = positions.indexOf(this.selfPosition);
        return positions[(m + n) % positions.length];
    }

    protected get lhoPosition() {
        return this.clockwise(1);
    }

    protected get partnerPosition() {
        return this.clockwise(2);
    }

    protected get rhoPosition() {
        return this.clockwise(3);
    }
}
