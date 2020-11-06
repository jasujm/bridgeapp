import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import GameSelector from "@/components/GameSelector.vue"
import Vuex from "vuex"
import sinon from "sinon"

const uuid = "6bac87b3-8e49-4675-bf69-8c0d6a351f40";

describe("GameSelector.vue", function() {
    let stubApi: any;
    let store: any;
    let state: any;
    let wrapper: any;

    this.beforeEach(function() {
        stubApi = {
            createGame: sinon.stub().resolves(uuid),
            joinGame: sinon.stub().resolves(),
        }
        state = { username: "user", api: stubApi };
        store = new Vuex.Store({
            state,
        });
        wrapper = mount(GameSelector, { localVue, store });
    });

    it("should create a game when requested", async function() {
        await wrapper.find("#create-game").trigger("click");
        expect(stubApi.createGame).to.be.called;
    });

    it("should not join a game if UUID is invalid", async function() {
        await wrapper.find("#join-game").trigger("click");
        expect(stubApi.joinGame).not.to.be.called;
    });

    describe("join game", function() {
        this.beforeEach(async function() {
            wrapper.find("#game-uuid").setValue(uuid);
            await wrapper.find("#join-game").trigger("click");
            await wrapper.vm.$nextTick();
        });

        it("should send API request", async function() {
            expect(stubApi.joinGame).to.be.calledWith(uuid);
        });

        it("should emit an event", async function() {
            expect(wrapper.emitted("game-joined")).to.be.deep.equal([[uuid]]);
        });
    });
});
