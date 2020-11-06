import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import Login from "@/components/Login.vue"
import sinon from "sinon"
import Vuex from "vuex"

describe("Login.vue", function() {
    let store: any;
    let actions: any;

    this.beforeEach(function() {
        actions = { login: sinon.fake() };
        store = new Vuex.Store({
            actions,
        });
    });

    it("should handle user login", function() {
        const wrapper = mount(Login, { localVue, store });
        wrapper.find("#username").setValue("user");
        wrapper.find("button").trigger("click");
        expect(actions.login).to.be.called;
    })
})
