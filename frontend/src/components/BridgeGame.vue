<template>
    <div class="bridge-game">
        <p>Your game: {{ game.uuid }}</p>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'BridgeGame',
    data: function() {
        return {
            game: {}
        }
    },
    mounted: async function() {
        let response = await axios.post(
            "http://localhost:8000/api/v1/games",
            {},
            {
                auth: {
                    username: "user",
                    password: "pass",
                },
            },
        );
        this.game = response.data;
    }
}
</script>
