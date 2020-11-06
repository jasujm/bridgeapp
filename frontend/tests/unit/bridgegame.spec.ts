import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import BridgeGame from "@/components/BridgeGame.vue"
import Vuex from "vuex"
import sinon from "sinon"

const uuid = "6bac87b3-8e49-4675-bf69-8c0d6a351f40";

describe("BridgeGame.vue", function() {
    let stubApi: any;
    let store: any;
    let state: any;

    this.beforeEach(function() {
        stubApi = {
            createGame: sinon.stub().resolves(uuid),
            joinGame: sinon.stub().resolves(),
        }
        state = { username: "user", api: stubApi };
        store = new Vuex.Store({
            state,
        });
    });

    it("should create a game when requested", async function() {
        const wrapper = mount(BridgeGame, { localVue, store });
        await wrapper.find("#create-game").trigger("click");
        expect(stubApi.createGame).to.be.called;
    });

    it("should not join a game if UUID is invalid", async function() {
        const wrapper = mount(BridgeGame, { localVue, store });
        await wrapper.find("#join-game").trigger("click");
        expect(stubApi.joinGame).not.to.be.called;
    });

    it("should join a game when requested", async function() {
        const wrapper = mount(BridgeGame, { localVue, store });
        wrapper.find("#game-uuid").setValue(uuid);
        await wrapper.find("#join-game").trigger("click");
        expect(stubApi.joinGame).to.be.calledWith(uuid);
    });
});
