import { localVue, expect } from "./common"
import { mount, Wrapper } from "@vue/test-utils"
import CardDisplay from "@/components/CardDisplay.vue"
import { Rank, Suit } from "@/api/types"

const card = { rank: Rank._4, suit: Suit.clubs };

describe("CardDisplay.vue", function() {
    describe("card actions", function() {
        let wrapper: Wrapper<CardDisplay>;

        this.beforeEach(function() {
            wrapper = mount(CardDisplay, { localVue, propsData: card });
        });

        it("should display the card", async function() {
            expect(wrapper.classes()).to.be.contain(`rank-${card.rank}`)
                .and.to.contain(`suit-${card.suit}`);
        });

        it("should not play card when pressed and not active", async function() {
            await wrapper.trigger("mousedown");
            expect(wrapper.emitted("play")).to.be.undefined;
        });

        it("should play card when pressed", async function() {
            wrapper.setProps({ allowed: true });
            await wrapper.vm.$nextTick();
            await wrapper.trigger("mousedown");
            expect(wrapper.emitted("play")).to.be.deep.equal([[card]]);
        });
    });
});
