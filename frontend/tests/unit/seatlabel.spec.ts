import { localVue, expect } from "./common";
import { mount, Wrapper } from "@vue/test-utils";
import SeatLabel from "@/components/SeatLabel.vue";
import { Position } from "@/api/types";

const playerId = "313343df-3c97-42aa-a4f3-3abe10ced3b0";
const username = "user";
const player = { id: playerId, username };
const position = Position.north;

describe("SeatLabel.vue", function () {
  let wrapper: Wrapper<SeatLabel>;

  this.beforeEach(async function () {
    wrapper = mount(SeatLabel, { localVue, propsData: { player, position } });
    await wrapper.vm.$nextTick();
  });

  it("should display player name and position", function () {
    expect(wrapper.find(".player").text()).to.contain(username);
  });

  it("should display position when there is no player in the seat", async function () {
    wrapper.setProps({ player: null });
    await wrapper.vm.$nextTick();
    expect(wrapper.find(".position.north").exists()).to.be.true;
  });
});
