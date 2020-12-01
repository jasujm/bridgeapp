<template>
<div class="bridge-game">
    <b-alert :variant="errorVariant" :show="showError">{{ errorMessage }}</b-alert>
    <b-alert variant="info" :show="!$store.getters.isLoggedIn">Login to get started.</b-alert>
    <GameSelector ref="selector" @game-joined="updateGame($event)" />
    <BridgeTable ref="table" v-if="hasGame" :gameUuid="this.$route.params.gameUuid" />
</div>
</template>

<script lang="ts">
import { Vue, Component, Ref } from "vue-property-decorator"
import GameSelector from "@/components/GameSelector.vue"
import BridgeTable from "@/components/BridgeTable.vue"

@Component({
    components: {
        GameSelector,
        BridgeTable,
    }
})
export default class BridgeGame extends Vue {
    @Ref() readonly selector!: GameSelector;
    @Ref() readonly table!: BridgeTable;

    private updateGame(gameUuid: string) {
        if (gameUuid != this.$route.params.gameUuid) {
            this.$router.push({ name: "games", params: { gameUuid }});
        }
        if (this.table) {
            this.table.refresh();
        }
    }

    private get hasGame() {
        return Boolean(this.$route.params.gameUuid);
    }

    private get showError() {
        return this.$store.state.error.message != "";
    }

    private get errorVariant() {
        return this.$store.state.error.severity;
    }

    private get errorMessage() {
        return this.$store.state.error.message;
    }

    mounted() {
        const gameUuid = this.$route.params.gameUuid;
        if (gameUuid) {
            this.selector.setUuid(gameUuid);
        }
    }
}
</script>
