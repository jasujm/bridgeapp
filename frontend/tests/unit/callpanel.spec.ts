import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import CallPanel from "@/components/CallPanel.vue"
import { CallType, Strain, Call } from "@/api/types"
import Vuex from "vuex"
import sinon from "sinon"

const gameUuid = "73395eef-2e4a-4908-9e06-f36ad747f3b3"
const bid = { level: 1, strain: Strain.clubs };

function makePropsData(call: Call) {
    return {
        gameUuid,
        allowedCalls: [
            call,
        ]
    };
}

describe("CallPanel.vue", function() {
    const calls = [
        { type: CallType.pass },
        { type: CallType.double },
        { type: CallType.redouble },
        { type: CallType.bid, bid },
    ]
    let stubApi: any;
    let store: any;
    let state: any;

    this.beforeEach(function() {
        stubApi = {
            makeCall: sinon.stub().resolves(),
        }
        state = { username: "user", api: stubApi };
        store = new Vuex.Store({
            state,
        });
    });

    describe("call actions", function() {
        for (const call of calls) {
            describe(call.type, function() {
                let wrapper: any;

                this.beforeEach(function() {
                    const propsData = makePropsData(call);
                    wrapper = mount(CallPanel, { localVue, store, propsData });
                });

                it("should have button if allowed", function() {
                    const button = wrapper.find(`button .call.${call.type}`);
                    expect(button.exists()).to.be.true;
                });
                it("should make call when the button is pressed", async function() {
                    const button = wrapper.find("button");
                    await button.trigger("click");
                    expect(stubApi.makeCall).to.be.calledWith(gameUuid, call);
                });
            });
        }

        it("should not allow calls if game is not set", async function() {
            const propsData = makePropsData({ type: CallType.pass });
            propsData.gameUuid = "";
            const wrapper = mount(CallPanel, { localVue, store, propsData });
            await wrapper.find("button").trigger("click");
            expect(stubApi.makeCall).not.to.be.called;
        });
    });
});
