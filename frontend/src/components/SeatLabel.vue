<template>
<strong class="seat-label">
    <span v-if="player && playerUsername" class="player" :class="position">{{ playerLabel }}</span>
    <PositionDisplay v-else :position="position" />
</strong>
</template>

<script lang="ts">
import { Vue, Component, Prop, Watch } from "vue-property-decorator";
import { Position } from "@/api/types"
import { positionAbbrev } from "./position"
import PositionDisplay from "./PositionDisplay.vue"

@Component({
    components: {
        PositionDisplay,
    }
})
export default class PlayerLabel extends Vue {
    @Prop() private readonly player!: string | null;
    @Prop() private readonly position!: Position;
    private playerUsername = "";

    private get playerLabel() {
        return `${this.playerUsername} (${positionAbbrev(this.position)})`
    }

    @Watch("player", { immediate: true })
    private async updatePlayer(value: string | null) {
        if (value) {
            const api = this.$store.state.api;
            const { username } = await api.getPlayer(value);
            this.playerUsername = username;
        } else {
            this.playerUsername = "";
        }
    }
}
</script>
