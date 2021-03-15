import { Vue, Component, Prop } from "vue-property-decorator"
import { Rank } from "@/api/types"
import { rankClass, rankText } from "./rankdisplay"

@Component
export default class RankDisplayMixin extends Vue {
    @Prop() protected readonly rank!: Rank;

    protected get rankClass() {
        return rankClass(this.rank);
    }

    protected get rankText() {
        return rankText(this.rank);
    }
}
