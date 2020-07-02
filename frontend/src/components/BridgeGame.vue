<template>
    <div class="bridge-game">
        <h2>Welcome {{ playerAccount.username }}</h2>
        <p>Game: {{ game.uuid }}</p>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'BridgeGame',
    props: ['playerAccount'],
    data () {
        return {
            game: {}
        }
    },
    watch: {
        // There must be a better way to trigger an event on login
        // than passing around and watching a properties...
        playerAccount: {
            immediate: true,
            handler: async function (account) {
                let response = await axios.post(
                    "http://localhost:8000/api/v1/games",
                    {},
                    {
                        auth: account,
                    },
                );
                this.game = response.data;
            }
        },
    },
}
</script>
