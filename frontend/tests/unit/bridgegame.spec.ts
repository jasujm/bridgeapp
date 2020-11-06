import { expect, localVue } from "./common"
import { shallowMount } from "@vue/test-utils"
import BridgeGame from "@/components/BridgeGame.vue"
import GameSelector from "@/components/GameSelector.vue"
import BridgeTable from "@/components/BridgeTable.vue"

const gameUuid = "6bac87b3-8e49-4675-bf69-8c0d6a351f40";

describe("BridgeGame.vue", function() {
    it("should join the selected game", async function() {
        const wrapper = shallowMount(BridgeGame, { localVue });
        const gameSelector = wrapper.findComponent(GameSelector);
        gameSelector.vm.$emit("game-joined", gameUuid);
        await wrapper.vm.$nextTick();
        expect(wrapper.findComponent(BridgeTable).exists()).to.be.true;
    });
});
