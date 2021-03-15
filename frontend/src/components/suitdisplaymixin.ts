import { Vue, Component, Prop } from "vue-property-decorator"
import { Suit } from "@/api/types"

const suitTexts = {
    clubs: "&clubs;",
    diamonds: "&diams;",
    hearts: "&hearts;",
    spades: "&spades;",
};

@Component
export default class SuitDisplayMixin extends Vue {
    @Prop() protected readonly suit!: Suit;

    protected get suitText() {
        return suitTexts[this.suit] || "?";
    }
}
