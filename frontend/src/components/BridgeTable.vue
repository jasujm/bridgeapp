<template>
<div class="bridge-table">
    <pre>{{ deal }}</pre>
</div>
</template>

<script lang="ts">
import { Vue, Component, Prop, Watch } from "vue-property-decorator"

@Component
export default class BridgeTable extends Vue {
    @Prop() private readonly gameUuid!: string;
    private deal = {};

    private async fetchGameState() {
        if (this.gameUuid) {
            const api = this.$store.state.api;
            this.deal = await api.getDeal(this.gameUuid);
        }
    }

    async mounted() {
        await this.fetchGameState();
        setInterval(this.fetchGameState, 5000);
    }

    @Watch("gameUuid")
    async fetchGameStateOnNewGame() {
        await this.fetchGameState();
    }
}
</script>
