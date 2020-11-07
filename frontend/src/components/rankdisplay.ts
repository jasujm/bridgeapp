import { Vue, Component } from "vue-property-decorator"
import { Rank } from "@/api/types"

@Component
export default class RankDisplayMixin extends Vue {
    protected rankText(rank: Rank) {
        switch (rank) {
            case Rank.ace:
                return "A";
            case Rank.king:
                return "K";
            case Rank.queen:
                return "Q";
            case Rank.jack:
                return "J";
        }
        return rank;
    }
}