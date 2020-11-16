import { Vue, Component } from "vue-property-decorator"
import { Rank } from "@/api/types"

const rankTexts: Partial<Record<Rank, string>> = {
    ace: "A",
    king: "K",
    queen: "Q",
    jack: "J",
}

@Component
export default class RankDisplayMixin extends Vue {
    protected rankClass(rank: Rank) {
        return rank.replace(/^(?=\d)/, "_");
    }

    protected rankText(rank: Rank) {
        return rankTexts[rank] || rank;
    }
}
