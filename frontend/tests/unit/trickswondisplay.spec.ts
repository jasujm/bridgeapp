import { localVue, expect } from "./common"
import { mount, Wrapper } from "@vue/test-utils"
import TricksWonDisplay from "@/components/TricksWonDisplay.vue"
import { Position } from "@/api/types"

describe("TricksWonDisplay.vue", function() {
    it("should initially display no tricks for either side", function() {
        const wrapper = mount(TricksWonDisplay, { localVue });
        expect(wrapper.find(".us .tricks").text()).to.be.equal("0");
        expect(wrapper.find(".them .tricks").text()).to.be.equal("0");
    });

    describe("tricks", function() {
        const tricks = [
            { winner: Position.north },
            { winner: Position.east },
            { winner: Position.south },
            { winner: Position.west },
            { winner: null },
        ];
        let wrapper: Wrapper<TricksWonDisplay>;

        this.beforeEach(function() {
            const propsData = { tricks };
            wrapper = mount(TricksWonDisplay, { localVue, propsData });
        });

        it("should count tricks for the north-south partnership", function() {
            expect(wrapper.find(".north.south .tricks").text()).to.be.equal("2");
        });

        it("should count tricks for the east-west partnership", function() {
            expect(wrapper.find(".east.west .tricks").text()).to.be.equal("2");
        });
    });
});
