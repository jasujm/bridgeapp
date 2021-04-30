import { localVue, expect } from "./common";
import { mount } from "@vue/test-utils";
import TrickDisplay from "@/components/TrickDisplay.vue";
import { Position, Rank, Suit } from "@/api/types";

describe("TrickDisplay.vue", function () {
  it("should have no cards if there are none played", function () {
    const wrapper = mount(TrickDisplay, { localVue });
    expect(wrapper.find(".card").exists()).to.be.false;
  });
  it("should display cards played in the trick", function () {
    const propsData = {
      trick: {
        cards: [
          {
            position: Position.south,
            card: { rank: Rank._10, suit: Suit.hearts },
          },
          {
            position: Position.west,
            card: { rank: Rank._7, suit: Suit.clubs },
          },
        ],
      },
    };
    const wrapper = mount(TrickDisplay, { localVue, propsData });
    expect(wrapper.find(".card-display.rank-10.suit-hearts").exists()).to.be
      .true;
    expect(wrapper.find(".card-display.rank-7.suit-clubs").exists()).to.be.true;
  });
});
