<template>
<div id="app">
    <b-alert show variant="warning">
        This app is still work in progress. Although playable, there are
        obvious quirks. I may also reset the app and data without a
        prior warning.
    </b-alert>
    <div class="container">
        <header>
            <Login class="float-right" />
            <h1>Play contract bridge</h1>
        </header>
        <main>
            <RouterView />
        </main>
        <footer>
            <small>
                Copyright &copy; <a href="https://www.jmoisio.eu/about/">Jaakko
                Moisio</a> 2020&ndash;2021. The application is open source and
                available
                in <a href="https://github.com/jasujm/bridgeapp">GitHub</a>.
            </small>
        </footer>
    </div>
</div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import Login from "./components/Login.vue";

@Component({
  components: {
    Login,
  },
})
export default class App extends Vue {}
</script>
