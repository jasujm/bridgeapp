import { localVue, expect } from "./common";
import { mount, Wrapper } from "@vue/test-utils";
import SearchGamesForm from "@/components/SearchGamesForm.vue";
import Vuex from "vuex";
import sinon from "sinon";
import flushPromises from "flush-promises";
import { PlayersInGame } from "@/api/types";

const name = "my game";
const gameId = "6bac87b3-8e49-4675-bf69-8c0d6a351f40";
const gameUrl = `http://testserver/api/v1/games/${gameId}`;

describe("SearchGamesForm.vue", function () {
  let clock: any;
  let fakeApi: any;
  let store: any;
  let state: any;
  let wrapper: Wrapper<SearchGamesForm>;

  this.beforeEach(function () {
    clock = sinon.useFakeTimers();
    fakeApi = {
      searchGames: sinon.fake.resolves([
        {
          id: gameId,
          self: gameUrl,
          name,
          players: new PlayersInGame(),
        },
      ]),
      joinGame: sinon.fake.resolves(null),
    };
    state = { api: fakeApi };
    store = new Vuex.Store({
      state,
    });
    wrapper = mount(SearchGamesForm, { localVue, store });
  });

  this.afterEach(function () {
    clock.restore();
  });

  describe("search games", function () {
    this.beforeEach(async function () {
      const inputWrapper = wrapper.find("input");
      inputWrapper.setValue(name);
      inputWrapper.trigger("keyup");
      clock.tick(200);
      await flushPromises();
    });

    it("should call the API endpoint", function () {
      expect(fakeApi.searchGames).to.be.calledWith(name);
    });

    it("should display results", function () {
      expect(wrapper.find(".games-list .game-summary").text()).to.include(name);
    });

    it("should emit an event when the game is selected", async function () {
      await wrapper.find(".games-list .game-summary button").trigger("click");
      expect(wrapper.emitted("game-selected")).to.be.deep.equal([[gameId]]);
    });
  });
});
