<template>
<span class="position" :class="position">{{ positionText(position) }}</span>
</template>

<script lang="ts">
import Component, { mixins } from "vue-class-component"
import { Prop } from "vue-property-decorator"
import PositionMixin from "./position"
import { Position } from "@/api/types"

@Component
export default class PositionDisplay extends mixins(PositionMixin) {
    @Prop() private readonly position!: Position;
}
</script>
