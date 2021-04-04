import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import Bidding from "@/components/Bidding.vue"
import { Position, CallType, Bid, Strain } from "@/api/types"

function makeCall(position: Position, type: CallType, bid?: Bid) {
    return {
        position,
        call: {
            type,
            bid,
        }
    };
}

function makeCalls(type: CallType, bid?: Bid) {
    return {
        calls: [
            makeCall(Position.north, type, bid),
        ],
    };
}

const bid = { level: 1, strain: Strain.clubs };

describe("Bidding.vue", function() {
    it("should have no call elements if there are no calls", function() {
        const wrapper = mount(Bidding, { localVue });
        expect(wrapper.find(".call").exists()).to.be.false;
    });

    const calls = [
        {
            propsData: makeCalls(CallType.bid, bid),
            expectedClass: ".type-bid .bid.strain-clubs.level-1",
        },
        { propsData: makeCalls(CallType.pass), expectedClass: ".type-pass" },
        { propsData: makeCalls(CallType.double), expectedClass: ".type-double" },
        { propsData: makeCalls(CallType.redouble), expectedClass: ".type-redouble" },
    ]

    for (const { propsData, expectedClass } of calls) {
        it(`should display ${propsData.calls[0].call.type}`, function() {
            const wrapper = mount(Bidding, { localVue, propsData });
            expect(wrapper.find(`.position-north .call${expectedClass}`).exists()).to.be.true;
        });
    }

    it("should display north south vulnerability", function() {
        const propsData = { northSouthVulnerable: true };
        const wrapper = mount(Bidding, { localVue, propsData });
        expect(wrapper.find(".vulnerable .north").exists()).to.be.true;
        expect(wrapper.find(".vulnerable .south").exists()).to.be.true;
    });

    it("should display east west vulnerability", function() {
        const propsData = { eastWestVulnerable: true };
        const wrapper = mount(Bidding, { localVue, propsData });
        expect(wrapper.find(".vulnerable .east").exists()).to.be.true;
        expect(wrapper.find(".vulnerable .west").exists()).to.be.true;
    });
});
