<template>
<div class="bridge-game">
    <GameSelector @game-joined="gameUuid = $event" />
    <BridgeTable v-if="hasGame" :gameUuid="gameUuid" />
</div>
</template>

<script lang="ts">
import Vue from "vue"
import Component from "vue-class-component"
import GameSelector from "./GameSelector.vue"
import BridgeTable from "./BridgeTable.vue"

@Component({
    components: {
        GameSelector,
        BridgeTable,
    }
})
export default class BridgeGame extends Vue {
    private readonly gameUuid = "";

    private get hasGame() {
        return Boolean(this.gameUuid);
    }
}
</script>
