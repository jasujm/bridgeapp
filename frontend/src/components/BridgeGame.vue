<template>
    <div class="bridge-game">
        <h2>Welcome {{ playerAccount.username }}</h2>
        <p><button type="button" v-on:click="createNewGame()">New game</button></p>
        <p>
            <input type="text" name="gameUuid" v-model="gameUuid" placeholder="UUID" />
            <button type="button" v-on:click="joinGame()">Join game</button>
        </p>
        <div v-if="dealState" class="self">
            <p>Position: {{ selfState.position }}</p>
            <div v-if="selfState.allowedCalls.length" class="calls">
                <button v-for="call in selfState.allowedCalls" :key="call" v-on:click="makeCall(call)">{{ call }}</button>
            </div>
            <div v-if="selfState.allowedCards.length" class="cards">
                <button v-for="card in selfState.allowedCards" :key="card" v-on:click="makeCard(card)">{{ card }}</button>
            </div>
        </div>
        <pre>{{ dealState }}</pre>
    </div>
</template>

<script>
import axios from 'axios'
import _ from 'lodash'

export default {
    name: 'BridgeGame',
    props: ['playerAccount'],
    data () {
        return {
            gameUuid: "",
            dealState: null,
            selfState: null,
            websocket: null,
        }
    },
    methods: {
        createNewGame: async function () {
            let response = await axios.post(
                this.getApiUrl("/games"),
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
                this.getApiUrl(`/games/${this.gameUuid}/players`),
                {},
                {
                    auth: this.playerAccount,
                },
            );
            this.websocket = new WebSocket(this.getWebsocketUrl(`/games/${this.gameUuid}/ws`));
            this.websocket.onmessage = _.debounce(this.updateState, 50);
            this.updateState();
        },
        updateState: async function () {
            let response = await axios.get(
                this.getApiUrl(`/games/${this.gameUuid}`),
                {
                    auth: this.playerAccount,
                },
            );
            this.dealState = response.data.deal;
            response = await axios.get(
                this.getApiUrl(`/games/${this.gameUuid}/self`),
                {
                    auth: this.playerAccount,
                },
            );
            this.selfState = response.data;
        },
        makeCall: async function (call) {
            await axios.post(
                this.getApiUrl(`/games/${this.gameUuid}/calls`),
                call,
                {
                    auth: this.playerAccount,
                },
            );
        },
        makeCard: async function (card) {
            await axios.post(
                this.getApiUrl(`/games/${this.gameUuid}/trick`),
                card,
                {
                    auth: this.playerAccount,
                },
            );
        },
        getApiUrl (route) {
            return `${process.env.VUE_APP_BRIDGEAPP_API_PREFIX || ""}/api/v1${route}`
        },
        getWebsocketUrl (route) {
            const prefix = process.env.VUE_APP_BRIDGEAPP_WEBSOCKET_PREFIX || `wss://${location.host}`;
            return `${prefix}/api/v1${route}`;
        },
    }
}
</script>
