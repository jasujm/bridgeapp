<template>
    <div class="bridge-game">
        <h2>Welcome {{ playerAccount.username }}</h2>
        <p><button type="button" v-on:click="createNewGame()">New game</button></p>
        <p>
            <input type="text" name="gameUuid" v-model="gameUuid" placeholder="UUID" />
            <button type="button" v-on:click="joinGame()">Join existing game</button>
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
                "/api/v1/games",
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
                `/api/v1/games/${this.gameUuid}/players`,
                {},
                {
                    auth: this.playerAccount,
                },
            );
            setInterval(this.updateState, 3000);
        },
        updateState: async function () {
            let response = await axios.get(
                `/api/v1/games/${this.gameUuid}`,
                {
                    auth: this.playerAccount,
                },
            );
            this.dealState = response.data.deal;
            response = await axios.get(
                `/api/v1/games/${this.gameUuid}/self`,
                {
                    auth: this.playerAccount,
                },
            );
            this.selfState = response.data;
        },
        makeCall: async function (call) {
            await axios.post(
                `/api/v1/games/${this.gameUuid}/calls`,
                call,
                {
                    auth: this.playerAccount,
                },
            );
            this.updateState();
        },
        makeCard: async function (card) {
            await axios.post(
                `/api/v1/games/${this.gameUuid}/trick`,
                card,
                {
                    auth: this.playerAccount,
                },
            );
            this.updateState();
        },
    }
}
</script>
