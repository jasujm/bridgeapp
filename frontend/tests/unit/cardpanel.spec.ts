import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import CardPanel from "@/components/CardPanel.vue"
import { Rank, Suit } from "@/api/types"
import Vuex from "vuex"
import sinon from "sinon"
import _ from "lodash"

const gameUuid = "73395eef-2e4a-4908-9e06-f36ad747f3b3"

const allowedCards = [
    { rank: Rank._4, suit: Suit.clubs },
    { rank: Rank._9, suit: Suit.diamonds },
    { rank: Rank.king, suit: Suit.clubs },
];

describe("CardPanel.vue", function() {
    let fakeApi: any;
    let store: any;
    let state: any;

    this.beforeEach(function() {
        fakeApi = {
            playCard: sinon.fake.resolves(null),
        }
        state = { username: "user", api: fakeApi };
        store = new Vuex.Store({
            state,
        });
    });

    describe("card actions", function() {
        let wrapper: any;

        this.beforeEach(function() {
            const propsData = { gameUuid, allowedCards };
            wrapper = mount(CardPanel, { localVue, store, propsData });
        });

        it("should have buttons sorted by suit and rank", function() {
            const classes = wrapper.findAll("button").wrappers.
                map((w: any) => w.find(".card-display").classes());
            expect(classes.length).to.be.equal(3);
            expect(classes[0]).to.include("rank-king").and.to.include("suit-clubs");
            expect(classes[1]).to.include("rank-4").and.to.include("suit-clubs");
            expect(classes[2]).to.include("rank-9").and.to.include("suit-diamonds");
        });
        it("should play card when the button is pressed", async function() {
            const button = wrapper.find("button");
            await button.trigger("click");
            expect(fakeApi.playCard).to.be.calledWith(gameUuid, _.last(allowedCards));
        });
    });

    it("should not allow play if game is not set", async function() {
        const propsData = { allowedCards };
        const wrapper = mount(CardPanel, { localVue, store, propsData });
        await wrapper.find("button").trigger("click");
        expect(fakeApi.playCard).not.to.be.called;
    });
});
