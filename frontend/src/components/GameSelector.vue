<template>
<div class="game-selector">
    <p>
        Please enter the UUID of the game and click “Go”. Or to create a new
        game, click “+”. After creating a game, you can just share the URL of
        the page with your three bridge buddies.
    </p>
    <validation-observer v-slot="{ handleSubmit }" slim>
        <b-form @submit.prevent="handleSubmit(selectGame)">
            <validation-provider name="Game UUID" rules="required|uuid" v-slot="validationContext">
                <b-form-group :disabled="!$store.getters.isLoggedIn">
                    <b-input-group>
                        <b-button
                            variant="secondary"
                            @click="createGame()">+</b-button>
                        <b-form-input
                            id="game-id"
                            placeholder="Game UUID"
                            v-model="gameId"
                            :state="getValidationState(validationContext)"
                            aria-describedby="game-id-feedback"
                            ></b-form-input>
                        <b-button
                            type="submit"
                            variant="primary">Go</b-button>
                        <b-form-invalid-feedback id="game-id-feedback">
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
    private gameId = "";

    setGameId(gameId: string) {
        this.gameId = gameId;
    }

    async createGame() {
        const game = await this.$store.state.api.createGame();
        this.gameId = game.id;
        await this.$store.state.api.joinGame(game.id);
        await this.selectGame();
    }

    async selectGame() {
        this.$emit("game-selected", this.gameId);
    }
}
</script>
