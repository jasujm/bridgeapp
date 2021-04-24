<template>
<div class="search-games-form">
    <b-form-group>
        <b-form-input
            v-model="q"
            placeholder="Search games"
            @keyup="searchGames()">
        </b-form-input>
    </b-form-group>
    <ul v-show="hasGames" class="games-list">
        <li class="game-summary" v-for="game in games" :key="game.id">
            <b-button
                class="join-game"
                size="sm"
                variant="success"
                @click="selectGame(game.id)">Select</b-button>
            <strong>{{ game.name }}</strong>
        </li>
    </ul>
</div>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator"
import { GameSummary } from "@/api/types"
import _ from "lodash"

@Component
export default class SearchGamesForm extends Vue {
    private q = "";
    private games: Array<GameSummary> = [];

    private get hasGames() {
        return this.q && !_.isEmpty(this.games);
    }

    private selectGame(gameId: string) {
        this.$emit("game-selected", gameId);
    }

    private _searchGames() {
        if (this.q) {
            this.$store.state.api.searchGames(this.q).then(
                (games: Array<GameSummary>) => this.games = games
            ).catch((err: Error) => this.$store.dispatch("reportError", err));
        } else {
            this.games = [];
        }
    }

    private searchGames = _.debounce(this._searchGames, 100);
}
</script>

<style lang="scss" scoped>
@import "~bootstrap/scss/functions";
@import "~bootstrap/scss/variables";
@import "~bootstrap/scss/mixins";
@import "../styles/mixins";

ul.games-list {
  @include bulletless-list;

  border: 1px solid $dark;
  border-radius: 2px;
  background-color: $light;

  li {
    overflow: auto;
    padding: 0.3rem;
    width: auto;
    border-top: 1px solid $gray-400;

    &:first-child {
      border: 0;
    }

    .join-game {
      float: right;
    }
  }
}
</style>
