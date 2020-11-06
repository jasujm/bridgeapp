<template>
<div class="bridge-game">
    <p>Hello, {{ $store.state.username }}! Let's play bridge.</p>
    <p><b-button id="create-game" v-on:click="createGame()">Create game</b-button></p>
    <p v-if="uuid">Playing: {{ uuid }}</p>
</div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator"
import Api from "@/api"

@Component
export default class BridgeGame extends Vue {
    uuid: string | null = null;
    api = new Api();

    mounted() {
        this.api.authenticate(this.$store.state.username);
    }

    async createGame() {
        const response = await this.api.createGame();
        this.uuid = response.uuid;
    }
}
</script>
