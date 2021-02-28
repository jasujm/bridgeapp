import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
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

    this.beforeEach(function() {
        api = {
            createPlayer: sinon.fake.resolves(player),
        };
        actions = { login: sinon.fake() };
        store = new Vuex.Store({
            state: { api },
            actions,
        });
    });

    it("should handle user login", async function() {
        const wrapper = mount(Login, { localVue, store });
        wrapper.find("#username").setValue("user");
        await wrapper.find("form").trigger("submit");
        await flushPromises();
        expect(api.createPlayer).to.be.calledWith(player.username);
        expect(actions.login).to.be.calledWith(sinon.match.any, player.id);
    });
})
