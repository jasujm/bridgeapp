import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import BridgeTable from "@/components/BridgeTable.vue"
import Vuex from "vuex"
import sinon from "sinon"
import { Position, Rank, Suit, Deal, Self, EventHandlers, CallType } from "@/api/types"
import flushPromises from "flush-promises"
import _ from "lodash"

const gameUuid = "6bac87b3-8e49-4675-bf69-8c0d6a351f40";

describe("BridgeTable.vue", function() {
    let fakeApi: any;
    let self: Self;
    let deal: Deal;
    let store: any;
    let state: any;
    let wrapper: any;

    this.beforeEach(async function() {
        self = new Self();
        deal = new Deal();
        fakeApi = {
            getDeal: sinon.fake.resolves(deal),
            getSelf: sinon.fake.resolves(self),
            subscribe: sinon.fake(),
        }
        state = { username: "user", api: fakeApi };
        store = new Vuex.Store({
            state,
        });
        wrapper = mount(BridgeTable, { localVue, store, propsData: { gameUuid } });
    });

    it("should fetch game data when mounted", async function() {
        expect(fakeApi.subscribe).to.be.calledWith(gameUuid);
        expect(fakeApi.getDeal).to.be.calledWith(gameUuid);
        expect(fakeApi.getSelf).to.be.calledWith(gameUuid);
    });

    it("should fetch game data when game is changed", async function() {
        const otherUuid = "1e994843-c6e8-4751-9151-b23d44814b8e"
        wrapper.setProps({ gameUuid: otherUuid });
        await flushPromises();
        expect(fakeApi.subscribe).to.be.calledWith(otherUuid);
        expect(fakeApi.getDeal).to.be.calledWith(otherUuid);
        expect(fakeApi.getSelf).to.be.calledWith(otherUuid);
    });

    describe("turn", function() {
        for (const position of _.values(Position)) {
            it(`should display turn marker for ${position}`, async function() {
                const deal = new Deal();
                deal.positionInTurn = position;
                wrapper.setData({ deal });
                await wrapper.vm.$nextTick();
                expect(wrapper.find(`.${position}.turn`).exists()).to.be.true;
            });
        }
    });

    describe("events", function() {
        let handlers: EventHandlers;
        const trickCards = { cards: [] };

        this.beforeEach(function() {
            handlers = fakeApi.subscribe.getCall(0).lastArg;
        });

        it("should update deal status on deal event", async function() {
            handlers.deal!({ game: gameUuid, type: "deal" });
            expect(fakeApi.getDeal).to.be.called;
        });

        it("should update allowed actions on turn event", async function() {
            self.position = Position.south;
            self.allowedCalls = [{ type: CallType.pass }];
            self.allowedCards = [{ rank: Rank._2, suit: Suit.clubs }];
            // Self has turn... fetch new actions
            handlers.turn!({ game: gameUuid, type: "turn", position: Position.south });
            expect(fakeApi.getSelf).to.be.called;
            expect(wrapper.vm.deal.positionInTurn).to.be.equal(Position.south);
            expect(wrapper.vm.self.allowedCalls).to.be.equal(self.allowedCalls);
            expect(wrapper.vm.self.allowedCards).to.be.equal(self.allowedCards);
            // Someone else has turn... clear the actions
            handlers.turn!({ game: gameUuid, type: "turn", position: Position.north });
            expect(wrapper.vm.deal.positionInTurn).to.be.equal(Position.north);
            expect(wrapper.vm.self.allowedCalls).to.be.empty;
            expect(wrapper.vm.self.allowedCards).to.be.empty;
        });

        it("should add call on call event", async function() {
            const position = Position.east;
            const call = { type: CallType.pass };
            handlers.call!({ game: gameUuid, type: "call", position, call });
            expect(wrapper.vm.deal.calls).to.deep.include({ position, call });
        });

        describe("play", function() {
            const position = Position.west;
            const card = { rank: Rank.jack, suit: Suit.diamonds };

            this.beforeEach(function() {
                deal.tricks.push(trickCards);
                deal.cards.west.push(card);
                wrapper.setData({ deal });
            });

            it("should add the played card to the trick", function() {
                handlers.play!({ game: gameUuid, type: "play", position, card });
                expect(wrapper.vm.deal.tricks[0].cards).to.deep.include({ position, card });
            });

            it("should remove the played card from the hand", function() {
                handlers.play!({ game: gameUuid, type: "play", position, card });
                expect(wrapper.vm.deal.cards.west).to.be.empty;
            });

            it("should remove the played card from the hand even if unknown", function() {
                deal.cards.west[0] = null;
                wrapper.setData({ deal });
                handlers.play!({ game: gameUuid, type: "play", position, card });
                expect(wrapper.vm.deal.cards.west).to.be.empty;
            });
        });

        it("should reveal dummy on dummy event", function() {
            const position = Position.east;
            const cards = [{ rank: Rank.queen, suit: Suit.hearts }];
            handlers.dummy!({ game: gameUuid, type: "dummy", position, cards });
            expect(wrapper.vm.deal.cards.east).to.be.deep.equal(cards);
        });

        it("should add a new trick on trick event", function() {
            handlers.trick!({ game: gameUuid, type: "trick" });
            expect(wrapper.vm.deal.tricks).to.have.deep.members([trickCards]);
        });

        it("should not add a new trick if there are 13", function() {
            deal.tricks = Array(13).fill(trickCards);
            wrapper.setData({ deal });
            handlers.trick!({ game: gameUuid, type: "trick" });
            expect(wrapper.vm.deal.tricks.length).to.be.equal(13);
        });
    });
});
