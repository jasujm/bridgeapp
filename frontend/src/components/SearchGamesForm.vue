<template>
  <div class="search-games-form">
    <b-form-group>
      <b-form-input
        v-model="q"
        placeholder="Search games"
        @keyup="searchGames()"
      >
      </b-form-input>
    </b-form-group>
    <ul v-show="hasGames" class="games-list">
      <li class="game-summary" v-for="game in games" :key="game.id">
        <b-button
          class="join-game"
          variant="success"
          @click="selectGame(game.id)"
          >Select</b-button
        >
        <b-row no-gutters>
          <b-col cols="12"
            ><strong>{{ game.name }}</strong></b-col
          >
        </b-row>
        <b-row no-gutters>
          <b-col
            v-for="{ position, username } in playerList(game.players)"
            :key="`${position}-${username}`"
            sm="3"
          >
            <PositionDisplay :position="position" />: {{ username }}
          </b-col>
        </b-row>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { GameSummary, PlayersInGame, Position, Player } from "@/api/types";
import PositionDisplay from "./PositionDisplay.vue";
import _ from "lodash";

@Component({
  components: {
    PositionDisplay,
  },
})
export default class SearchGamesForm extends Vue {
  private q = "";
  private games: Array<GameSummary> = [];

  private get hasGames() {
    return this.q && !_.isEmpty(this.games);
  }

  private playerList(players: PlayersInGame) {
    //  typescript doesn't understand that filter removes non-null
    //  players, so perform a cast to suppress warning
    return _.values(Position)
      .filter((position) => players[position] !== null)
      .map((position) => ({
        position,
        username: (players[position] as Player).username,
      }));
  }

  private selectGame(gameId: string) {
    this.$emit("game-selected", gameId);
  }

  private _searchGames() {
    if (this.q) {
      this.$store.state.api
        .searchGames(this.q)
        .then((games: Array<GameSummary>) => (this.games = games))
        .catch((err: Error) => this.$store.dispatch("reportError", err));
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
