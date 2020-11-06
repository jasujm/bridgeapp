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
    it("should display bids", function() {
        const propsData = makeCalls(CallType.bid, bid);
        const wrapper = mount(Bidding, { localVue, propsData });
        expect(wrapper.find(".call.bid.strain-clubs.level-1").exists()).to.be.true;
    });
    it("should display passes", function() {
        const propsData = makeCalls(CallType.pass);
        const wrapper = mount(Bidding, { localVue, propsData });
        expect(wrapper.find(".call.pass").exists()).to.be.true;
    });
    it("should display doubles", function() {
        const propsData = makeCalls(CallType.double);
        const wrapper = mount(Bidding, { localVue, propsData });
        expect(wrapper.find(".call.double").exists()).to.be.true;
    });
    it("should display redoubles", function() {
        const propsData = makeCalls(CallType.redouble);
        const wrapper = mount(Bidding, { localVue, propsData });
        expect(wrapper.find(".call.redouble").exists()).to.be.true;
    });
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
});
