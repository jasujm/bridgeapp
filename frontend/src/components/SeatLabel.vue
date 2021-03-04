<template>
<span class="player">{{ seatLabel }}</span>
</template>

<script lang="ts">
import { Vue, Component, Prop, Watch } from "vue-property-decorator";
import { Position } from "@/api/types"
import { positionAbbrev, positionText } from "./position"

@Component
export default class PlayerLabel extends Vue {
    @Prop() private readonly player!: string | null;
    @Prop() private readonly position!: Position;
    private playerUsername = "";

    private get seatLabel() {
        if (this.player && this.playerUsername) {
            return `${this.playerUsername} (${positionAbbrev(this.position)})`
        } else {
            return positionText(this.position);
        }
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
