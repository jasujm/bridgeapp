<template>
<div class="bridge-game">
    <ErrorDisplay :severity="$store.state.error.severity" :message="$store.state.error.message" />
    <b-alert variant="info" :show="!$store.getters.isLoggedIn">Login to get started.</b-alert>
    <GameSelector ref="selector" @game-selected="updateGame($event)" />
    <BridgeTable ref="table" v-if="hasGame" :gameId="this.$route.params.gameId" />
</div>
</template>

<script lang="ts">
import { Vue, Component, Ref } from "vue-property-decorator"
import ErrorDisplay from "@/components/ErrorDisplay.vue"
import GameSelector from "@/components/GameSelector.vue"
import BridgeTable from "@/components/BridgeTable.vue"

@Component({
    components: {
        ErrorDisplay,
        GameSelector,
        BridgeTable,
    }
})
export default class BridgeGame extends Vue {
    @Ref() readonly selector!: GameSelector;
    @Ref() readonly table!: BridgeTable;

    private updateGame(gameId: string) {
        if (gameId != this.$route.params.gameId) {
            this.$router.push({ name: "games", params: { gameId }});
        }
        if (this.table) {
            this.table.refresh();
        }
    }

    private get hasGame() {
        return Boolean(this.$route.params.gameId);
    }

    mounted() {
        const gameId = this.$route.params.gameId;
        if (gameId) {
            this.selector.setGameId(gameId);
        }
    }
}
</script>
