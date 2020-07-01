<template>
    <div class="app">
        <h1>Bridge app!</h1>
        <BridgeGame />
    </div>
</template>

<script>
import BridgeGame from './components/BridgeGame.vue'

export default {
    name: 'App',
    components: {
        BridgeGame
    }
}
</script>
