import { localVue, expect } from "./common"
import { mount, Wrapper } from "@vue/test-utils"
import DealResultsDisplay from "@/components/DealResultsDisplay.vue"
import { NIL as deal } from "uuid"
import { Partnership } from "@/api/types"

describe("DealResultsDisplay.vue", function() {
    const results = [
        { deal, result: { partnership: Partnership.northSouth, score: 200 } },
        { deal, result: { partnership: Partnership.eastWest, score: 420 } },
        { deal, result: { partnership: null, score: 0 } },
    ];
    let wrapper: Wrapper<DealResultsDisplay>;

    this.beforeEach(function() {
        wrapper = mount(
            DealResultsDisplay, { localVue, propsData: { results } }
        );
    });

    it("it should have one row per result", function() {
        expect(wrapper.findAll(".result").length).to.be.equal(3);
    });

    it("it should display score for north south", function() {
        expect(
            wrapper.find(".result:nth-of-type(1) .score.north-south").text()
        ).to.be.equal("200");
    });

    it("it should display score for east west", function() {
        expect(
            wrapper.find(".result:nth-of-type(2) .score.east-west").text()
        ).to.be.equal("420");
    });

    it("it should display score for passed out deal", function() {
        expect(
            wrapper.
                find(".result:nth-of-type(3)").
                findAll(".score").
                wrappers.
                map(w => w.text())
        ).to.be.deep.equal(["0", "0"]);
    });
});
