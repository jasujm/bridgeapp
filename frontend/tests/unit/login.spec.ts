import { localVue, expect } from "./common"
import { mount, Wrapper } from "@vue/test-utils"
import Login from "@/components/Login.vue"
import sinon from "sinon"
import Vuex from "vuex"
import flushPromises from "flush-promises"

const player = {
    id: "acf5ea8f-03c2-450b-81c9-7edaa97b9793",
    username: "user",
};

describe("Login.vue", function() {
    let api: any;
    let store: any;
    let actions: any;
    let wrapper: Wrapper<Login>;

    this.beforeEach(function() {
        api = {
            createPlayer: sinon.stub().resolves(player),
            getPlayer: sinon.fake.resolves(player),
        };
        actions = { login: sinon.fake() };
        store = new Vuex.Store({
            state: { api },
            actions,
        });
        wrapper = mount(Login, { localVue, store });
    });

    it("should create player on login", async function() {
        wrapper.find("#username").setValue("user");
        await wrapper.find("form").trigger("submit");
        await flushPromises();
        expect(api.createPlayer).to.be.calledWith(player.username);
        expect(actions.login).to.be.calledWith(sinon.match.any, player.id);
    });

    it("should get the existing player if it exists", async function() {
        api.createPlayer.rejects({ isAxiosError: true, response: { status: 409 } });
        wrapper.find("#username").setValue("user");
        await wrapper.find("form").trigger("submit");
        await flushPromises();
        expect(api.createPlayer).to.be.calledWith(player.username);
        expect(api.getPlayer).to.be.calledWith(player.username);
        expect(actions.login).to.be.calledWith(sinon.match.any, player.id);
    });
})
