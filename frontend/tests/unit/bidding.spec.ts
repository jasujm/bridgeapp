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
            expectedClass: ".bid.strain-clubs.level-1",
        },
        { propsData: makeCalls(CallType.pass), expectedClass: ".pass" },
        { propsData: makeCalls(CallType.double), expectedClass: ".double" },
        { propsData: makeCalls(CallType.redouble), expectedClass: ".redouble" },
    ]

    for (const { propsData, expectedClass } of calls) {
        it(`should display ${propsData.calls[0].call.type}`, function() {
            const wrapper = mount(Bidding, { localVue, propsData });
            expect(wrapper.find(`.call${expectedClass}`).exists()).to.be.true;
        });
    }

    it("should tabulate calls", function() {
        const propsData = {
            calls: [
                makeCall(Position.east, CallType.pass),
                makeCall(Position.south, CallType.pass),
                makeCall(Position.west, CallType.bid),
                makeCall(Position.north, CallType.pass),
            ]
        }
        const wrapper = mount(Bidding, { localVue, propsData });
        expect(wrapper.findAll("tbody tr").length).to.be.equal(2);
    });

    it("should display north south vulnerability", function() {
        const propsData = { northSouthVulnerable: true };
        const wrapper = mount(Bidding, { localVue, propsData });
        expect(wrapper.find(".north.vulnerable").exists()).to.be.true;
        expect(wrapper.find(".south.vulnerable").exists()).to.be.true;
    });

    it("should display east west vulnerability", function() {
        const propsData = { eastWestVulnerable: true };
        const wrapper = mount(Bidding, { localVue, propsData });
        expect(wrapper.find(".east.vulnerable").exists()).to.be.true;
        expect(wrapper.find(".west.vulnerable").exists()).to.be.true;
    });
});