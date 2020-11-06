import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import BridgeTable from "@/components/BridgeTable.vue"
import Vuex from "vuex"
import sinon from "sinon"
import { Deal, Self } from "@/api/types"

const gameUuid = "6bac87b3-8e49-4675-bf69-8c0d6a351f40";

describe("BridgeTable.vue", function() {
    let stubApi: any;
    let store: any;
    let state: any;
    let wrapper: any;

    this.beforeEach(async function() {
        stubApi = {
            getDeal: sinon.stub().resolves(new Deal()),
            getSelf: sinon.stub().resolves(new Self()),
        }
        state = { username: "user", api: stubApi };
        store = new Vuex.Store({
            state,
        });
        wrapper = mount(BridgeTable, { localVue, store, propsData: { gameUuid } });
        await wrapper.vm.$nextTick();
    });

    it("should fetch game data when mounted", async function() {
        expect(stubApi.getDeal).to.be.calledWith(gameUuid);
        expect(stubApi.getSelf).to.be.calledWith(gameUuid);
    });

    it("should fetch game data when game is changed", async function() {
        const otherUuid = "1e994843-c6e8-4751-9151-b23d44814b8e"
        wrapper.setProps({ gameUuid: otherUuid });
        await wrapper.vm.$nextTick();
        expect(stubApi.getDeal).to.be.calledWith(otherUuid);
        expect(stubApi.getSelf).to.be.calledWith(otherUuid);
    });
});
