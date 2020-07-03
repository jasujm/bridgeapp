<template>
    <div class="bridge-game">
        <h2>Welcome {{ playerAccount.username }}</h2>
        <p><button type="button" v-on:click="createNewGame()">New game</button></p>
        <p>
            <input type="text" name="gameUuid" v-model="gameUuid" placeholder="UUID" />
            <button type="button" v-on:click="joinGame()">Join existing game</button>
        </p>
        <pre>{{ dealState }}</pre>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'BridgeGame',
    props: ['playerAccount'],
    data () {
        return {
            gameUuid: "",
            dealState: null,
            selfState: null,
        }
    },
    methods: {
        createNewGame: async function () {
            let response = await axios.post(
                "http://localhost:8000/api/v1/games",
                {},
                {
                    auth: this.playerAccount,
                },
            );
            this.gameUuid = response.data.uuid;
            this.dealState = response.data.deal;
        },
        joinGame: async function () {
            await axios.post(
                `http://localhost:8000/api/v1/games/${this.gameUuid}/players`,
                {},
                {
                    auth: this.playerAccount,
                },
            );
            await this.updateState();
        },
        updateState: async function () {
            let response = await axios.get(
                `http://localhost:8000/api/v1/games/${this.gameUuid}`,
                {
                    auth: this.playerAccount,
                },
            );
            this.dealState = response.data.deal;
        },
    }
}
</script>
