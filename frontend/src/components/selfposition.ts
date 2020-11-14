import { Vue, Component, Prop } from "vue-property-decorator"
import { Position } from "@/api/types"
import { clockwise } from "@/utils"

@Component
export default class SelfPositionMixin extends Vue {
    @Prop({ default: Position.north }) protected readonly selfPosition!: Position;

    protected get lhoPosition() {
        return clockwise(this.selfPosition, 1);
    }

    protected get partnerPosition() {
        return clockwise(this.selfPosition, 2);
    }

    protected get rhoPosition() {
        return clockwise(this.selfPosition, 3);
    }
}
