import { Vue, Component, Prop } from "vue-property-decorator"
import { Rank } from "@/api/types"
import { rankText } from "./rankdisplay"

@Component
export default class RankDisplayMixin extends Vue {
    @Prop() protected readonly rank!: Rank;

    protected get rankText() {
        return rankText(this.rank);
    }
}
