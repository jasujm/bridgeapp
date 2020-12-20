import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import GameSelector from "@/components/GameSelector.vue"
import Vuex from "vuex"
import sinon from "sinon"
import flushPromises from "flush-promises"

const gameId = "6bac87b3-8e49-4675-bf69-8c0d6a351f40";
const gameUrl = `http://testserver/api/v1/games/${gameId}`;

describe("GameSelector.vue", function() {
    let fakeApi: any;
    let store: any;
    let state: any;
    let wrapper: any;

    this.beforeEach(function() {
        fakeApi = {
            createGame: sinon.fake.resolves({ id: gameId, self: gameUrl }),
            joinGame: sinon.fake.resolves(null),
        }
        state = { username: "user", api: fakeApi };
        store = new Vuex.Store({
            state,
            getters: { isLoggedIn: () => true },
        });
        wrapper = mount(GameSelector, { localVue, store });
    });

    it("should create a game when requested", async function() {
        await wrapper.find(".btn-secondary").trigger("click");
        await flushPromises();
        expect(fakeApi.createGame).to.be.called;
        expect(fakeApi.joinGame).to.be.calledWith(gameId);
    });

    it("should not join a game if UUID is invalid", async function() {
        await wrapper.find("form").trigger("submit");
        await flushPromises();
        expect(wrapper.emitted("game-selected")).to.be.undefined;
    });

    describe("join game", function() {
        this.beforeEach(async function() {
            wrapper.find("#game-id").setValue(gameId);
            await wrapper.find("form").trigger("submit");
            await flushPromises();
        });

        it("should emit an event", async function() {
            expect(wrapper.emitted("game-selected")).to.be.deep.equal([[gameId]]);
        });
    });
});
