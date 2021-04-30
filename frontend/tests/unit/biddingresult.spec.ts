import { localVue, expect } from "./common";
import { mount, Wrapper } from "@vue/test-utils";
import BiddingResult from "@/components/BiddingResult.vue";
import { Strain, Doubling, Position } from "@/api/types";

describe("BiddingResult.vue", function () {
  const declarers = [Position.north, Position.west];
  const contracts = [
    {
      bid: { level: 4, strain: Strain.spades },
      doubling: Doubling.undoubled,
    },
    {
      bid: { level: 2, strain: Strain.clubs },
      doubling: Doubling.doubled,
    },
    {
      bid: { level: 7, strain: Strain.notrump },
      doubling: Doubling.redoubled,
    },
  ];

  for (const declarer of declarers) {
    for (const contract of contracts) {
      describe(`${declarer} ${contract.bid.level} ${contract.bid.strain} ${contract.doubling}`, function () {
        let wrapper: Wrapper<BiddingResult>;

        this.beforeEach(function () {
          const propsData = { declarer, contract };
          wrapper = mount(BiddingResult, { localVue, propsData });
        });

        it("should display declarer", function () {
          expect(wrapper.find(".declarer").classes()).to.include(declarer);
        });

        it("should display contract bid", function () {
          expect(wrapper.find(".contract .bid").classes()).to.include.members([
            `level-${contract.bid.level}`,
            `strain-${contract.bid.strain}`,
          ]);
        });

        it("should display contract doubling", function () {
          expect(wrapper.find(".contract .doubling").classes()).to.include(
            contract.doubling
          );
        });
      });
    }
  }
});
