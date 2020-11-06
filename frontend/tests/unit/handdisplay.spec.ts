import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import HandDisplay from "@/components/HandDisplay.vue"
import { Suit, Rank } from "@/api/types"

describe("HandDisplay.vue", function() {
    it("should have no card lists if there are no cards", function() {
        const wrapper = mount(HandDisplay, { localVue });
        expect(wrapper.find(".card-list").exists()).to.be.false;
    });
    it("should display label", function() {
        const propsData = { label: "Cards" };
        const wrapper = mount(HandDisplay, { localVue, propsData });
        expect(wrapper.text()).to.include("Cards");
    });
    it("should display cards grouped by suit", function() {
        const propsData = {
            cards: [
                { suit: Suit.diamonds, rank: Rank._7 },
                { suit: Suit.diamonds, rank: Rank._2 },
                { suit: Suit.spades, rank: Rank.ace },
            ]
        };
        const wrapper = mount(HandDisplay, { localVue, propsData });
        expect(wrapper.find(".card-list.suit-diamonds .rank-7").exists()).to.be.true;
        expect(wrapper.find(".card-list.suit-diamonds .rank-2").exists()).to.be.true;
        expect(wrapper.find(".card-list.suit-spades .rank-ace").exists()).to.be.true;
    });
    it("should not display unknown cards", function() {
        const propsData = {
            cards: [null, null, null]
        };
        const wrapper = mount(HandDisplay, { localVue, propsData });
        expect(wrapper.find(".card-list").exists()).to.be.false;
    });
});
