import { localVue, expect } from "./common";
import { mount, Wrapper } from "@vue/test-utils";
import LoginForm from "@/components/LoginForm.vue";
import sinon from "sinon";
import Vuex from "vuex";
import flushPromises from "flush-promises";

const username = "user";
const password = "secret";

const player = {
  id: "acf5ea8f-03c2-450b-81c9-7edaa97b9793",
  username,
};

describe("LoginForm.vue", function () {
  let api: any;
  let store: any;
  let actions: any;
  let wrapper: Wrapper<LoginForm>;

  this.beforeEach(function () {
    api = {
      getPlayer: sinon.fake.resolves(player),
    };
    actions = { login: sinon.fake() };
    store = new Vuex.Store({
      state: { api },
      actions,
    });
    wrapper = mount(LoginForm, { localVue, store });
  });

  it("should not send incomplete form", async function () {
    wrapper.find("input[type=text]").setValue(username);
    await wrapper.find("form").trigger("submit");
    await flushPromises();
    expect(actions.login).not.to.be.called;
  });

  it("should login player", async function () {
    wrapper.find("input[type=text]").setValue(username);
    wrapper.find("input[type=password]").setValue(password);
    await wrapper.find("form").trigger("submit");
    await flushPromises();
    expect(actions.login).to.be.calledWith(sinon.match.any, {
      username,
      password,
    });
  });
});
