import chai from "chai"
import { createLocalVue, mount } from "@vue/test-utils"
import Login from "@/components/Login.vue"
import { BootstrapVue } from "bootstrap-vue"
import sinon from "sinon"
import sinonChai from "sinon-chai"
import Vuex from "vuex"

chai.use(sinonChai);
const expect = chai.expect;

const localVue = createLocalVue()
localVue.use(BootstrapVue);
localVue.use(Vuex)

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
