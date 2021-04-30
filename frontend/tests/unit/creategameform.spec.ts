import { localVue, expect } from "./common";
import { mount } from "@vue/test-utils";
import CreateGameForm from "@/components/CreateGameForm.vue";
import Vuex from "vuex";
import sinon from "sinon";
import flushPromises from "flush-promises";

const name = "my game";
const gameId = "6bac87b3-8e49-4675-bf69-8c0d6a351f40";
const gameUrl = `http://testserver/api/v1/games/${gameId}`;

describe("CreateGameForm.vue", function () {
  let fakeApi: any;
  let store: any;
  let state: any;
  let wrapper: any;

  this.beforeEach(function () {
    fakeApi = {
      createGame: sinon.fake.resolves({ id: gameId, self: gameUrl, name }),
      joinGame: sinon.fake.resolves(null),
    };
    state = { api: fakeApi };
    store = new Vuex.Store({
      state,
    });
    wrapper = mount(CreateGameForm, { localVue, store });
  });

  it("should not create game without name", async function () {
    await wrapper.find("form").trigger("submit");
    await flushPromises();
    expect(fakeApi.createGame).not.to.be.called;
  });

  describe("submit form", function () {
    this.beforeEach(async function () {
      wrapper.find("input").setValue(name);
      await wrapper.find("form").trigger("submit");
      await flushPromises();
    });

    it("should create a game", function () {
      expect(fakeApi.createGame).to.be.calledWith(name);
    });

    it("should join the created game", function () {
      expect(fakeApi.joinGame).to.be.calledWith(gameId);
    });

    it("emit an event", function () {
      expect(wrapper.emitted("game-selected")).to.be.deep.equal([[gameId]]);
    });
  });
});
