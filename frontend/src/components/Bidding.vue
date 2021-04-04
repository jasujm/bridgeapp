<template>
<div class="bidding">
    <div class="d-flex positions">
        <div v-for="position in positions" class="position-cell" :class="positionClasses(position)">
            <PositionDisplay :position="position" />
        </div>
    </div>
    <div class="d-flex flex-wrap calls" :class="'player-position-' + playerPosition">
        <div v-for="(call, index) in calls" :key="index" class="call-cell" :class="callClasses(call)">
            <CallDisplay :type="call.call.type" :bid="call.call.bid" />
        </div>
        <div v-if="displayCallPanel" class="call-cell" :class="callPositionClasses(playerPosition)">
            <CallPanel :allowedCalls="allowedCalls" @call="$emit('call', $event)" />
        </div>
    </div>
</div>
</template>

<script lang="ts">
import Component, { mixins } from "vue-class-component"
import { Prop } from "vue-property-decorator"
import _ from "lodash"
import PositionDisplay from "./PositionDisplay.vue"
import CallDisplay from "./CallDisplay.vue"
import CallPanel from "./CallPanel.vue"
import { Position, Call, PositionCallPair } from "@/api/types"
import SelfPositionMixin from "./selfposition"

@Component({
    components: {
        PositionDisplay,
        CallDisplay,
        CallPanel,
    }
})
export default class Bidding extends mixins(SelfPositionMixin) {
    @Prop({ default: () => [] }) private readonly calls!: Array<PositionCallPair>;
    @Prop() private readonly positionInTurn?: Position;
    @Prop({ default: false }) private readonly northSouthVulnerable!: boolean;
    @Prop({ default: false }) private readonly eastWestVulnerable!: boolean;
    @Prop({ default: () => [] }) private readonly allowedCalls!: Array<Call>;

    private get positions() {
        return [
            this.lhoPosition,
            this.partnerPosition,
            this.rhoPosition,
            this.playerPosition,
        ];
    }

    private positionClasses(position: Position) {
        return {
            vulnerable: ([Position.north, Position.south].includes(position)) ?
                this.northSouthVulnerable : this.eastWestVulnerable,
        };
    }

    private callClasses(call: PositionCallPair) {
        return this.callPositionClasses(call.position);
    }

    private get displayCallPanel() {
        return !_.isEmpty(this.allowedCalls) &&
            this.positionInTurn == this.playerPosition;
    }

    private callPositionClasses(position: Position) {
        return `position-${position}`;
    }
}
</script>

<style lang="scss" scoped>
$positions: north east south west;

.bidding {
  .position-cell, .call-cell {
    width: 25%;
  }
  .positions {
    font-weight: bold;
  }
  .calls {
    // This is for offsetting the call sequence to the table columns based on the
    // player position and whoever starts the call sequence
    @for $i from 1 through length($positions) {
      @for $j from 1 through length($positions) {
        $margin: ((3 + $j - $i) % 4) * 25%;
        $player-position: nth($positions, $i);
        $position: nth($positions, $j);
        &.player-position-#{$player-position} .call-cell.position-#{$position}:first-child {
          margin-left: $margin;
        }
      }
    }
  }
  ::v-deep .call {
    font-size: 1.25em;
  }
  .vulnerable {
    color: var(--danger);
  }
}
</style>
