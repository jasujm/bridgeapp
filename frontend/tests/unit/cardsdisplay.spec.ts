import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import CardsDisplay from "@/components/CardsDisplay.vue"
import { Position, Cards } from "@/api/types"

describe("CardsDisplay.vue", function() {
    it("should assign players their seats", async function() {
        const propsData = { position: Position.south, cards: new Cards() };
        const wrapper = mount(CardsDisplay, { localVue, propsData });
        expect(wrapper.find(".self.south").exists()).to.be.true;
        expect(wrapper.find(".lho.west").exists()).to.be.true;
        expect(wrapper.find(".partner.north").exists()).to.be.true;
        expect(wrapper.find(".rho.east").exists()).to.be.true;
    });
});
