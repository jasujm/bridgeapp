<template>
    <div class="app">
        <h1>Bridge app!</h1>
        <BridgeGame v-bind:playerAccount="playerAccount" v-if="authenticated" />
        <LoginForm v-else />
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
