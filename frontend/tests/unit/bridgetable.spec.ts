import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import BridgeTable from "@/components/BridgeTable.vue"
import Vuex from "vuex"
import sinon from "sinon"
import { Position, Deal, Self } from "@/api/types"
import flushPromises from "flush-promises"
import _ from "lodash"

const gameUuid = "6bac87b3-8e49-4675-bf69-8c0d6a351f40";

describe("BridgeTable.vue", function() {
    let fakeApi: any;
    let store: any;
    let state: any;
    let wrapper: any;
    let clock: any;

    this.beforeEach(async function() {
        fakeApi = {
            getDeal: sinon.fake.resolves(new Deal()),
            getSelf: sinon.fake.resolves(new Self()),
            subscribe: sinon.fake(),
        }
        state = { username: "user", api: fakeApi };
        store = new Vuex.Store({
            state,
        });
        clock = sinon.useFakeTimers();
        wrapper = mount(BridgeTable, { localVue, store, propsData: { gameUuid } });
        clock.tick(100);
    });

    this.afterEach(function() {
        clock.restore();
    });

    it("should fetch game data when mounted", async function() {
        expect(fakeApi.subscribe).to.be.calledWith(gameUuid);
        expect(fakeApi.getDeal).to.be.calledWith(gameUuid);
        expect(fakeApi.getSelf).to.be.calledWith(gameUuid);
    });

    it("should fetch game data when game is changed", async function() {
        const otherUuid = "1e994843-c6e8-4751-9151-b23d44814b8e"
        wrapper.setProps({ gameUuid: otherUuid });
        // Fetching game data is debounced, and it was already triggered when
        // the component mounted. For some reason multiple flushes required in
        // addition to ticking ¯\_(ツ)_/¯
        await flushPromises();
        clock.tick(100);
        await flushPromises();
        expect(fakeApi.subscribe).to.be.calledWith(otherUuid);
        expect(fakeApi.getDeal).to.be.calledWith(otherUuid);
        expect(fakeApi.getSelf).to.be.calledWith(otherUuid);
    });

    describe("turn", function() {
        for (const position of _.values(Position)) {
            it(`should display turn marker for ${position}`, async function() {
                const deal = new Deal();
                deal.positionInTurn = position;
                wrapper.setData({ deal });
                await wrapper.vm.$nextTick();
                expect(wrapper.find(`.${position}.turn`).exists()).to.be.true;
            });
        }
    });
});
