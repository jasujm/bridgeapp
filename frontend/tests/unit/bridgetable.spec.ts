import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import BridgeTable from "@/components/BridgeTable.vue"
import Vuex from "vuex"
import sinon, { SinonSpy } from "sinon"
import {
    Position,
    Rank,
    Suit,
    Game,
    Deal,
    EventHandlers,
    CallType,
    Strain,
    Doubling,
    Partnership,
    DealEndEvent,
} from "@/api/types"
import flushPromises from "flush-promises"
import _ from "lodash"

const gameUuid = "6bac87b3-8e49-4675-bf69-8c0d6a351f40";
const playerUuid = "313343df-3c97-42aa-a4f3-3abe10ced3b0";
const otherPlayerUuid = "fb11eeae-7be2-41d6-a7f9-4dc126c2bf3c";

describe("BridgeTable.vue", function() {
    let clock: any;
    let fakeApi: any;
    let game: Game;
    let store: any;
    let state: any;
    let actions: any;
    let wrapper: any;

    this.beforeEach(async function() {
        clock = sinon.useFakeTimers();
        game = new Game();
        game.deal = new Deal();
        game.players.west = otherPlayerUuid;
        fakeApi = {
            getGame: sinon.fake.resolves({ game, counter: 0 }),
            getDeal: sinon.fake.resolves(game.deal),
            getPlayerState: sinon.stub().resolves(game.me),
            joinGame: sinon.fake.resolves(undefined),
            leaveGame: sinon.fake.resolves(undefined),
            makeCall: sinon.stub().resolves(),
            playCard: sinon.stub().resolves(),
            subscribe: sinon.fake(),
        }
        state = { username: "user", api: fakeApi };
        actions = { reportError: sinon.fake() };
        store = new Vuex.Store({
            state,
            actions,
            getters: { isLoggedIn: () => true },
        });
        wrapper = mount(
            BridgeTable, { localVue, store, propsData: { gameUuid } }
        );
        await flushPromises();
        clock.tick(200);
    });

    this.afterEach(function() {
        clock.restore();
    });

    it("should fetch game data when mounted", function() {
        expect(fakeApi.subscribe).to.be.calledWith(gameUuid);
        expect(fakeApi.getGame).to.be.calledWith(gameUuid);
    });

    it("should fetch game data when game is changed", async function() {
        const otherUuid = "1e994843-c6e8-4751-9151-b23d44814b8e"
        wrapper.setProps({ gameUuid: otherUuid });
        await flushPromises();
        clock.tick(200);
        expect(fakeApi.subscribe).to.be.calledWith(otherUuid);
        expect(fakeApi.getGame).to.be.calledWith(otherUuid);
    });

    describe("join", function() {
        it("should display join buttons when the player is not in the game", function() {
            expect(wrapper.find(".join-game.any").exists()).to.be.true;
        });
        it("should join the game when the join button is pressed", async function() {
            await wrapper.find(".join-game.any a").trigger("click");
            expect(fakeApi.joinGame).to.be.calledWith(gameUuid);
        });
        for (const position of [Position.north, Position.east, Position.south]) {
            it(`should display join buttons for available seats: ${position}`, function() {
                expect(wrapper.find(`.join-game.${position}`).exists()).to.be.true;
            });
            it(`should join the game when the join button is pressed: ${position}`, async function() {
                await wrapper.find(`.join-game.${position} a`).trigger("click");
                expect(fakeApi.joinGame).to.be.calledWith(gameUuid, position);
            });
        }
        it("should not display join button for unavailable seat", function() {
            expect(wrapper.find(".join-game.west").exists()).to.be.false;
        });
    });

    describe("leave", function() {
        this.beforeEach(async function() {
            game.players.north = playerUuid;
            game.me.position = Position.north;
            wrapper.setData({ me: game.me, players: game.players });
            await wrapper.vm.$nextTick();
        });

        it("should display leave buttons when the player is in the game", function() {
            expect(wrapper.find(".leave-game").exists()).to.be.true;
        });
        it("should leave the game when the leave button is pressed", async function() {
            await wrapper.find(".leave-game").trigger("click");
            expect(fakeApi.leaveGame).to.be.calledWith(gameUuid);
        });
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

    describe("calls", function() {
        const call = { type: CallType.pass };

        this.beforeEach(async function() {
            fakeApi.getPlayerState.resetHistory();
            game.me.allowedCalls = [call];
            await wrapper.vm.$nextTick();
        });

        it("should make call on call event", async function() {
            await wrapper.find(".call-panel button").trigger("click");
            expect(fakeApi.makeCall).to.be.calledWith(gameUuid, call);
        })

        it("should fetch player state on 409", async function() {
            fakeApi.makeCall.rejects({ isAxiosError: true, response: { status: 409 } });
            await wrapper.find(".call-panel button").trigger("click");
            await flushPromises();
            clock.tick(200);
            expect(fakeApi.getPlayerState).to.be.calledWith(gameUuid);
        });

        it("should let other errors through", async function() {
            fakeApi.makeCall.rejects();
            await wrapper.find(".call-panel button").trigger("click");
            await flushPromises();
            clock.tick(200);
            expect(fakeApi.getPlayerState).not.to.be.called;
            expect(actions.reportError).to.be.called;
        });
    });

    describe("cards", function() {
        const card = { rank: Rank._7, suit: Suit.diamonds };

        this.beforeEach(async function() {
            fakeApi.getPlayerState.resetHistory();
            game.me.allowedCards = [card];
            await wrapper.vm.$nextTick();
        });

        it("should make card on play event", async function() {
            await wrapper.find(".card-panel button").trigger("click");
            expect(fakeApi.playCard).to.be.calledWith(gameUuid, card);
        });

        it("should fetch player state on 409", async function() {
            fakeApi.playCard.rejects({ isAxiosError: true, response: { status: 409 } });
            await wrapper.find(".card-panel button").trigger("click");
            await flushPromises();
            clock.tick(200);
            expect(fakeApi.getPlayerState).to.be.calledWith(gameUuid);
        });

        it("should let other errors through", async function() {
            fakeApi.playCard.rejects();
            await wrapper.find(".card-panel button").trigger("click");
            await flushPromises();
            clock.tick(200);
            expect(fakeApi.getPlayerState).not.to.be.called;
            expect(actions.reportError).to.be.called;
        });
    });

    describe("events", function() {
        let handlers: EventHandlers;

        this.beforeEach(function() {
            wrapper.setData({ dealCounter: null });
            handlers = fakeApi.subscribe.getCall(0).lastArg;
        });

        it("should update players on player event", async function() {
            handlers.player!({
                game: gameUuid,
                type: "player",
                position: Position.north,
                player: playerUuid,
                counter: 1
            });
            await wrapper.vm.$nextTick();
            expect(wrapper.find(".join-game.north").exists()).to.be.false;
        });

        it("should update players on player event", async function() {
            handlers.player!({
                game: gameUuid,
                type: "player",
                position: Position.west,
                player: null,
                counter: 1
            });
            await wrapper.vm.$nextTick();
            expect(wrapper.find(`.join-game.west`).exists()).to.be.true;
        });

        it("should update deal status on deal event", async function() {
            handlers.deal!({ game: gameUuid, type: "deal", counter: 1 });
            expect(fakeApi.getDeal).to.be.called;
        });

        it("should update allowed actions on turn event", async function() {
            game.me.position = Position.south;
            game.me.allowedCalls = [{ type: CallType.pass }];
            game.me.allowedCards = [{ rank: Rank._2, suit: Suit.clubs }];
            // The player has turn... fetch new actions
            handlers.turn!(
                { game: gameUuid, type: "turn", position: Position.south, counter: 1 }
            );
            expect(fakeApi.getPlayerState).to.be.called;
            expect(wrapper.vm.deal.positionInTurn).to.be.equal(Position.south);
            expect(wrapper.vm.me.allowedCalls).to.be.equal(game.me.allowedCalls);
            expect(wrapper.vm.me.allowedCards).to.be.equal(game.me.allowedCards);
            // Someone else has turn... clear the actions
            handlers.turn!(
                { game: gameUuid, type: "turn", position: Position.north, counter: 2 }
            );
            expect(wrapper.vm.deal.positionInTurn).to.be.equal(Position.north);
            expect(wrapper.vm.me.allowedCalls).to.be.empty;
            expect(wrapper.vm.me.allowedCards).to.be.empty;
        });

        it("should add call on call event", async function() {
            const position = Position.east;
            const call = { type: CallType.pass };
            handlers.call!(
                { game: gameUuid, type: "call", position, call, counter: 1 }
            );
            expect(wrapper.vm.deal.calls).to.deep.include({ position, call });
        });

        describe("bidding", function() {
            const declarer = Position.south;
            const contract = {
                bid: { level: 2, strain: Strain.notrump },
                doubling: Doubling.undoubled,
            };

            this.beforeEach(function() {
                handlers.bidding!(
                    { game: gameUuid, type: "bidding", declarer, contract, counter: 1 }
                );
            });

            it("should record declarer on bidding event", function() {
                expect(wrapper.vm.deal.declarer).to.be.equal(declarer);
            });

            it("should record contract on bidding event", function() {
                expect(wrapper.vm.deal.contract).to.be.deep.equal(contract);
            })

            it("should open the first trick on bidding event", function() {
                expect(wrapper.vm.deal.tricks.length).to.be.equal(1);
            });
        })

        describe("play", function() {
            const position = Position.west;
            const card = { rank: Rank.jack, suit: Suit.diamonds };

            this.beforeEach(function() {
                game.deal!.tricks.push({ cards: [] });
                game.deal!.cards.west.push(card);
                wrapper.setData({ deal: game.deal });
            });

            it("should add the played card to the trick", function() {
                handlers.play!({ game: gameUuid, type: "play", position, card, counter: 1 });
                expect(wrapper.vm.deal.tricks[0].cards).to.deep.include({ position, card });
            });

            it("should remove the played card from the hand", function() {
                handlers.play!({ game: gameUuid, type: "play", position, card, counter: 1 });
                expect(wrapper.vm.deal.cards.west).to.be.empty;
            });

            it("should remove the played card from the hand even if unknown", function() {
                game.deal!.cards.west[0] = null;
                wrapper.setData({ deal: game.deal });
                handlers.play!({ game: gameUuid, type: "play", position, card, counter: 1 });
                expect(wrapper.vm.deal.cards.west).to.be.empty;
            });
        });

        it("should reveal dummy on dummy event", function() {
            const position = Position.east;
            const cards = [{ rank: Rank.queen, suit: Suit.hearts }];
            handlers.dummy!({ game: gameUuid, type: "dummy", position, cards, counter: 1 });
            expect(wrapper.vm.deal.cards.east).to.be.deep.equal(cards);
        });

        describe("trick", function() {
            const winner = Position.west;

            it("should add a new trick on trick event", function() {
                handlers.trick!({ game: gameUuid, type: "trick", winner, counter: 1 });
                expect(wrapper.vm.deal.tricks).to.have.deep.members([{ cards: [] }]);
            });

            it("should record the winner of the previous trick", function() {
                game.deal!.tricks = [{ cards: [] }];
                wrapper.setData({ deal: game.deal });
                handlers.trick!({ game: gameUuid, type: "trick", winner, counter: 1 });
                expect(wrapper.vm.deal.tricks[0].winner).to.be.equal(winner);
            });

            it("should not add a new trick if there are 13", function() {
                game.deal!.tricks = Array(13).fill({ cards: [] });
                wrapper.setData({ deal: game.deal });
                handlers.trick!({ game: gameUuid, type: "trick", winner, counter: 1 });
                expect(wrapper.vm.deal.tricks.length).to.be.equal(13);
            });

        });

        describe("dealend", function() {
            const dealUuid = "d7a05529-9b95-4678-b6b2-e5ca0ea501fc";
            const dealResult = {
                deal: dealUuid,
                result: { partnership: Partnership.northSouth, score: 200 },
            };
            let dealEndEvent: DealEndEvent;
            let toastSpy: SinonSpy;

            this.beforeEach(function() {
                dealEndEvent = {
                    game: gameUuid,
                    type: "dealend",
                    deal: dealUuid,
                    contract: null,
                    tricksWon: null,
                    result: dealResult.result,
                    counter: 1,
                }
                toastSpy = sinon.spy(wrapper.vm.$bvToast, "toast");
            });

            this.afterEach(function() {
                toastSpy.restore();
            });

            it("should add new deal result on dealend event", function() {
                handlers.dealend!(dealEndEvent);
                expect(wrapper.vm.results).to.be.deep.equal([dealResult]);
            });

            it("should display toast on dealend event", function() {
                handlers.dealend!(dealEndEvent);
                expect(toastSpy).to.be.called;
            });

            it("should amend the latest result if deal UUID matches", function() {
                wrapper.setData({
                    results: [{ deal: dealUuid, result: null }]
                });
                handlers.dealend!(dealEndEvent);
                expect(wrapper.vm.results).to.be.deep.equal([dealResult]);
            });
        });
    });
});
