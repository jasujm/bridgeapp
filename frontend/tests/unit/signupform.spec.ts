import { localVue, expect } from "./common"
import { mount, Wrapper } from "@vue/test-utils"
import SignupForm from "@/components/SignupForm.vue"
import sinon from "sinon"
import Vuex from "vuex"
import flushPromises from "flush-promises"

const username = "username";
const password = "secret";

const player = {
    id: "acf5ea8f-03c2-450b-81c9-7edaa97b9793",
    username,
};

describe("SignupForm.vue", function() {
    let api: any;
    let store: any;
    let actions: any;
    let wrapper: Wrapper<SignupForm>;

    this.beforeEach(function() {
        api = {
            createPlayer: sinon.fake.resolves(player),
        };
        actions = { login: sinon.fake() };
        store = new Vuex.Store({
            state: { api },
            actions,
        });
        wrapper = mount(SignupForm, { localVue, store });
    });

    it("should not send incomplete form", async function() {
        wrapper.find("input[type=text]").setValue(username);
        wrapper.findAll("input[type=password]").setValue(password);
        await wrapper.find("form").trigger("submit");
        await flushPromises();
        expect(api.createPlayer).not.to.be.called;
        expect(actions.login).not.to.be.called;
    });

    describe("send form", function() {
        this.beforeEach(async function() {
            wrapper.find("input[type=text]").setValue(username);
            wrapper.findAll("input[type=password]").setValue(password);
            await wrapper.find("input[type=checkbox]").setChecked(true);
            await wrapper.find("form").trigger("submit");
            await flushPromises();
        });

        it("should create player", function() {
            expect(api.createPlayer).to.be.calledWith(username, password);
        });

        it("should log the player in", function() {
            expect(actions.login).to.be.calledWith(sinon.match.any, { username, password });
        });
    });
})
