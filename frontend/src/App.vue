<template>
    <div class="app">
        <p><strong>What is this?</strong> It is a work in
        progress <a href="https://github.com/jasujm/bridgeapp">contract
        bridge webapp</a>. You can play it, if you don't mind
        interfacing raw UUIDs and JSON as user interface. You can
        login with any credentials. The app will track you by the user
        name only. The users and games will be gone when I reset the
        server, which is regularly.</p>
        <BridgeGame v-bind:playerAccount="playerAccount"
        v-if="authenticated" /> <LoginForm v-else />
    </div>
</template>

<script>
import BridgeGame from './components/BridgeGame.vue'
import LoginForm from './components/LoginForm.vue'

export default {
    name: 'App',
    data() {
        return {
            authenticated: false,
            playerAccount: {
                username: "",
                password: "",
            },
        };
    },
    components: {
        BridgeGame,
        LoginForm,
    }
}
</script>
