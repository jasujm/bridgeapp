<template>
<div class="game-selector">
    <p>
        <span v-if="$store.state.username">Hello, {{ $store.state.username
        }}!</span>  Please enter the UUID of the game and click “Go”. Or to
        create a new game, click “+”. After creating a game, you can just share
        the URL of the page with your three bridge buddies.
    </p>
    <validation-observer v-slot="{ handleSubmit }" slim>
        <b-form @submit.prevent="handleSubmit(selectGame)">
            <validation-provider name="UUID" rules="required|uuid" v-slot="validationContext">
                <b-form-group :disabled="!$store.getters.isLoggedIn">
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
                            variant="primary">Go</b-button>
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
import _ from "lodash"

@Component
export default class GameSelector extends mixins(ValidationMixin) {
    private uuid = "";

    setUuid(uuid: string) {
        this.uuid = uuid;
    }

    async createGame() {
        // TODO: The UUID from the API response (URL) is parsed, just so that
        // the URL is constructed over and over again. Instead just pass the URL
        // around.
        const game = await this.$store.state.api.createGame();
        const gameUuid = _.first(/\/[0-9a-f-]+$/.exec(game.self));
        if (gameUuid) {
            this.uuid = gameUuid.substring(1);
            await this.$store.state.api.joinGame(this.uuid);
            await this.selectGame();
        }
    }

    async selectGame() {
        this.$emit("game-selected", this.uuid);
    }
}
</script>
