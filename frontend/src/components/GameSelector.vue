<template>
<div class="game-selector">
    <p>
        Hello, {{ $store.state.username }}! Let's play bridge. Please enter the
        UUID of the game and click “Join”. Or to create a new game (whose UUID
        you can share with your three friends), click “+”.
    </p>
    <validation-observer v-slot="{ handleSubmit }" slim>
        <b-form @submit.prevent="handleSubmit(joinGame)">
            <validation-provider name="UUID" rules="required|uuid" v-slot="validationContext">
                <b-form-group>
                    <b-input-group>
                        <b-button
                            variant="secondary"
                            @click="createGame()">+</b-button>
                        <b-form-input
                            id="game-uuid"
                            placeholder="Game UUID"
                            v-model="uuid"
                            :state="getValidationState(validationContext)"
                            aria-describedby="game-uuid-feedback"
                            ></b-form-input>
                        <b-button
                            type="submit"
                            variant="primary">Join</b-button>
                        <b-form-invalid-feedback id="game-uuid-feedback">
                            {{ validationContext.errors[0] }}
                        </b-form-invalid-feedback>
                    </b-input-group>
                </b-form-group>
            </validation-provider>
        </b-form>
    </validation-observer>
</div>
</template>

<script lang="ts">
import Component, { mixins } from "vue-class-component"
import { ValidationMixin } from "./validation"

@Component
export default class GameSelector extends mixins(ValidationMixin) {
    private uuid = "";

    async createGame() {
        const response = await this.$store.state.api.createGame();
        this.uuid = response.uuid;
        await this.joinGame();
    }

    async joinGame() {
        await this.$store.state.api.joinGame(this.uuid);
        this.$emit("game-joined", this.uuid);
    }
}
</script>
