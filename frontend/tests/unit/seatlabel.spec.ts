import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import SeatLabel from "@/components/SeatLabel.vue"
import { positionText } from "@/components/position"
import Vuex from "vuex"
import sinon from "sinon"
import { Position } from "@/api/types"

const playerId = "313343df-3c97-42aa-a4f3-3abe10ced3b0";
const username = "user";
const player = { id: playerId, username };
const position = Position.north;

describe("SeatLabel.vue", function() {
    let api: any;
    let store: any;
    let wrapper: any;

    this.beforeEach(async function() {
        api = {
            getPlayer: sinon.fake.resolves(player),
        };
        store = new Vuex.Store({
            state: { api }
        });
        wrapper = mount(
            SeatLabel, { localVue, store, propsData: { player: playerId, position } }
        )
        await wrapper.vm.$nextTick();
    });

    it("should fetch player info", function() {
        expect(api.getPlayer).to.be.calledWith(playerId);
    });

    it("should display player name and position", function() {
        expect(wrapper.find(".player").text()).to.contain(username);
    });

    it("should display position when there is no player in the seat", async function() {
        wrapper.setProps({ player: null });
        await wrapper.vm.$nextTick();
        expect(wrapper.find(".player").text()).to.contain(positionText(position));
    })
});
