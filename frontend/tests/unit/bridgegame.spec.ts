import { localVue, expect } from "./common"
import { mount, shallowMount } from "@vue/test-utils"
import BridgeGame from "@/components/BridgeGame.vue"
import Api from "@/api"
import Vuex from "vuex"
import sinon from "sinon"

describe("BridgeGame.vue", function() {
    let authenticate: any;
    let store: any;
    let state: any;

    this.beforeEach(function() {
        authenticate = sinon.spy(Api.prototype, "authenticate")
        state = { username: "user" };
        store = new Vuex.Store({
            state,
        });
    });

    this.afterEach(function() {
        authenticate.restore();
    });

    it("should authenticate API with logged in user", function() {
        shallowMount(BridgeGame, { localVue, store });
        expect(authenticate).to.be.calledWith("user");
    });

    it("should create a game when requested", async function() {
        const wrapper = mount(BridgeGame, { localVue, store });
        const stub = sinon.stub(wrapper.vm.$data.api, "createGame")
            .resolves({ uuid: "6bac87b3-8e49-4675-bf69-8c0d6a351f40" });
        await wrapper.find("#create-game").trigger("click");
        expect(stub).to.be.called;
    });
});
