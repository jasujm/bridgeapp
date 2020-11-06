<template>
<div class="game-selector">
    <p>Hello, {{ $store.state.username }}! Let's play bridge. Please enter the
    UUID of the game and click “Join game”. Or to create a new game (whose UUID
    you can share with your three friends), click “Create game”.</p>
    <div>
        <validation-provider name="UUID" rules="required|uuid" v-slot="validationContext">
            <b-form-group>
                <b-input-group>
                    <b-button
                        id="create-game"
                        variant="secondary"
                        @click="createGame()">Create game</b-button>
                    <b-form-input
                        id="game-uuid"
                        placeholder="Game UUID"
                        v-model="uuid"
                        :state="getValidationState(validationContext)"
                        aria-describedby="game-uuid-feedback"
                        ></b-form-input>
                    <b-button
                        id="join-game"
                        variant="primary"
                        @click="joinGame()">Join game</b-button>
                    <b-form-invalid-feedback id="game-uuid-feedback">
                        {{ validationContext.errors[0] }}
                    </b-form-invalid-feedback>
                </b-input-group>
            </b-form-group>
        </validation-provider>
    </div>
</div>
</template>

<script lang="ts">
import Component, { mixins } from "vue-class-component"
import { validate as validateUuid } from "uuid"
import { ValidationMixin } from "./validation"

@Component
export default class GameSelector extends mixins(ValidationMixin) {
    private uuid = "";

    async createGame() {
        const response = await this.$store.state.api.createGame();
        this.uuid = response.uuid;
    }

    async joinGame() {
        if (validateUuid(this.uuid)) {
            await this.$store.state.api.joinGame(this.uuid);
            this.$emit("game-joined", this.uuid);
        }
    }
}
</script>
