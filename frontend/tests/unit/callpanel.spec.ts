import { localVue, expect } from "./common"
import { mount } from "@vue/test-utils"
import CallPanel from "@/components/CallPanel.vue"
import { CallType, Strain, Call } from "@/api/types"

const bid = { level: 1, strain: Strain.clubs };

function makePropsData(call: Call) {
    return {
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

    describe("call actions", function() {
        for (const call of calls) {
            describe(call.type, function() {
                let wrapper: any;

                this.beforeEach(function() {
                    const propsData = makePropsData(call);
                    wrapper = mount(CallPanel, { localVue, propsData });
                });

                it("should have button if allowed", function() {
                    const button = wrapper.find("button .call");
                    expect(button.classes()).to.include(`type-${call.type}`);
                });
                it("should emit call event when the button is pressed", async function() {
                    const button = wrapper.find("button");
                    await button.trigger("click");
                    expect(wrapper.emitted("call")).to.be.deep.equal([[call]]);
                });
            });
        }
    });
});
