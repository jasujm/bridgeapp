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
        if (rank.match(/^\d+/)) {
            return `_${rank}`;
        }
        return rank;
    }

    protected rankText(rank: Rank) {
        const text = rankTexts[rank];
        if (text) {
            return text;
        }
        return rank;
    }
}
