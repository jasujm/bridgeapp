<template>
<div class="game-selector">
    <p>Use the following forms to create a new game or join an
    existing one. Once created, you can also access a game directly by
    sharing the URL of the page.</p>
    <p><em>Hint!</em> Type your username in the game search to find
    the tables you seated in.</p>
    <b-tabs content-class="mt-3">
        <b-tab title="Search games">
            <SearchGamesForm @game-selected="$emit('game-selected', $event)" />
        </b-tab>
        <b-tab title="Create game">
            <CreateGameForm @game-selected="$emit('game-selected', $event)" />
        </b-tab>
    </b-tabs>
</div>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator"
import SearchGamesForm from "./SearchGamesForm.vue"
import CreateGameForm from "./CreateGameForm.vue"

@Component({
    components: {
        SearchGamesForm,
        CreateGameForm,
    }
})
export default class GameSelector extends Vue {}
</script>
