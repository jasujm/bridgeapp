<template>
  <div id="app">
    <b-navbar variant="dark" type="dark">
      <b-navbar-nav>
        <b-nav-item :to="{ path: '/games' }">Play contract bridge</b-nav-item>
      </b-navbar-nav>
      <b-navbar-nav class="ml-auto">
        <b-nav-item-dropdown v-if="$store.getters.isLoggedIn" text="User" right>
          <b-dropdown-item :to="{ path: '/account' }">Account</b-dropdown-item>
          <b-dropdown-item @click="$store.dispatch('logout')"
            >Log out</b-dropdown-item
          >
        </b-nav-item-dropdown>
        <b-nav-item v-else right><Login /></b-nav-item>
      </b-navbar-nav>
    </b-navbar>
    <b-alert show variant="warning">
      This app is still work in progress. Although playable, there are obvious
      quirks. I may also reset the app and data without a prior warning.
    </b-alert>
    <div class="container">
      <main>
        <RouterView />
      </main>
      <footer>
        <small>
          Copyright &copy;
          <a href="https://www.jmoisio.eu/about/">Jaakko Moisio</a>
          2020&ndash;2021. The application is open source and available in
          <a href="https://github.com/jasujm/bridgeapp">GitHub</a>. By using
          this website you agree to our
          <a href="https://www.websitepolicies.com/policies/view/RTZfOT2W"
            >terms and conditions</a
          >
          and
          <a href="https://www.websitepolicies.com/policies/view/STbelXSV"
            >privacy policy</a
          >.
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
