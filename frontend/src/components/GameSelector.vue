<template>
<div class="game-selector">
    <p>
        Please enter the UUID of the game and click “Go”. Or to create a new
        game, click “+”. After creating a game, you can just share the URL of
        the page with your three bridge buddies.
    </p>
    <ValidatedForm :submitHandler="selectGame">
        <validatedFormGroup name="Game UUID" rules="required|uuid" v-slot="{ state }" no-label>
            <b-input-group>
                <b-button
                    variant="secondary"
                    @click="createGame()">+</b-button>
                <b-form-input
                    :state="state"
                    placeholder="Game UUID"
                    v-model="gameId">
                </b-form-input>
                <b-button
                    type="submit"
                    variant="primary">Go</b-button>
            </b-input-group>
        </ValidatedFormGroup>
    </ValidatedForm>
</div>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator"
import ValidatedForm from "./ValidatedForm.vue"
import ValidatedFormGroup from "./ValidatedFormGroup.vue"

@Component({
    components: {
        ValidatedForm,
        ValidatedFormGroup,
    }
})
export default class GameSelector extends Vue {
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
