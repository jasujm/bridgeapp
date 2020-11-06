<template>
<div id="app">
    <div class="container">
        <header>
            <h1>Play contract bridge</h1>
        </header>
        <b-alert show variant="warning">
            This app is still very much work in progress. Although sort of
            playable, don’t get surprised if there are issues, or if your game
            abruptly disappears.
        </b-alert>
        <main>
            <BridgeGame v-if="$store.getters.isLoggedIn" />
            <Login v-else />
        </main>
        <footer>
            <small>
                Copyright &copy; <a href="https://www.jmoisio.eu/about/">Jaakko
                Moisio</a> 2020. The application is open source and available
                in <a href="https://github.com/jasujm/bridgeapp">GitHub</a>.
            </small>
        </footer>
    </div>
</div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import BridgeGame from "./components/BridgeGame.vue";
import Login from "./components/Login.vue";

@Component({
  components: {
    BridgeGame,
    Login,
  },
})
export default class App extends Vue {}
</script>
