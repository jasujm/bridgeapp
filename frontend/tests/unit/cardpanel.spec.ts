import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import CardPanel from "@/components/CardPanel.vue"
import { Rank, Suit } from "@/api/types"

const allowedCards = [
    { rank: Rank._4, suit: Suit.clubs },
    { rank: Rank._9, suit: Suit.diamonds },
    { rank: Rank.king, suit: Suit.clubs },
];

describe("CardPanel.vue", function() {
    describe("card actions", function() {
        let wrapper: any;

        this.beforeEach(function() {
            const propsData = { allowedCards };
            wrapper = mount(CardPanel, { localVue, propsData });
        });

        it("should have buttons sorted by suit and rank", function() {
            const classes = wrapper.findAll("button").wrappers.
                map((w: any) => w.find(".card-display").classes());
            expect(classes.length).to.be.equal(3);
            expect(classes[0]).to.include("rank-king").and.to.include("suit-clubs");
            expect(classes[1]).to.include("rank-4").and.to.include("suit-clubs");
            expect(classes[2]).to.include("rank-9").and.to.include("suit-diamonds");
        });
        it("should play card when the button is pressed", async function() {
            const button = wrapper.find("button");
            await button.trigger("click");
            expect(wrapper.emitted("play")).to.be.deep.equal([[allowedCards[2]]]);
        });
    });
});
