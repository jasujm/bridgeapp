import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import TableDisplay from "@/components/TableDisplay.vue"
import { Position, Cards } from "@/api/types"

describe("TableDisplay.vue", function() {
    it("should assign players their seats", async function() {
        const propsData = { selfPosition: Position.south, cards: new Cards() };
        const wrapper = mount(TableDisplay, { localVue, propsData });
        expect(wrapper.find(".self.south").exists()).to.be.true;
        expect(wrapper.find(".lho.west").exists()).to.be.true;
        expect(wrapper.find(".partner.north").exists()).to.be.true;
        expect(wrapper.find(".rho.east").exists()).to.be.true;
    });
    it("should not display trick if none exists", function() {
        const wrapper = mount(TableDisplay, { localVue });
        expect(wrapper.find(".trick-display").exists()).to.be.false;
    });
    it("should display trick if it exists", function() {
        const propsData = { trick: { cards: [], winner: null } };
        const wrapper = mount(TableDisplay, { localVue, propsData });
        expect(wrapper.find(".trick-display").exists()).to.be.true;
    });
});
