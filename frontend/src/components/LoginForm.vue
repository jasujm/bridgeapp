<template>
    <div class="login-form">
        <h2>Login</h2>
        <input type="text" name="username" v-model="input.username" placeholder="Username" />
        <input type="password" name="password" v-model="input.password" placeholder="Password" />
        <button type="button" v-on:click="login()">Login</button>
    </div>
</template>

<script>
export default {
    name: 'LoginForm',
    data () {
        return {
            input: {
                username: "",
                password: "",
            }
        }
    },
    methods: {
        login () {
            // There must be a more elegant way to pass around user
            // credentials...
            this.$emit('update:authenticated', true);
            this.$parent.authenticated = true;
            this.$parent.playerAccount = {
                username: this.input.username,
                password: this.input.password,
            };
        }
    },
}
</script>
