<template>
  <strong class="seat-label">
    <span v-if="player" class="player" :class="position">{{
      playerLabel
    }}</span>
    <PositionDisplay v-else :position="position" />
  </strong>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator";
import { Position, Player } from "@/api/types";
import { positionAbbrev } from "./position";
import PositionDisplay from "./PositionDisplay.vue";

@Component({
  components: {
    PositionDisplay,
  },
})
export default class PlayerLabel extends Vue {
  @Prop() private readonly player!: Player | null;
  @Prop() private readonly position!: Position;

  private get playerLabel() {
    // safe to cast away null, since the v-if in the template
    // already ensures `player` is not null
    return `${(this.player as Player).username} (${positionAbbrev(
      this.position
    )})`;
  }
}
</script>
