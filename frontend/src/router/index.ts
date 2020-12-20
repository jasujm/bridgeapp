import Vue from 'vue'
import VueRouter, { RouteConfig } from "vue-router"
import BridgeGame from "../views/BridgeGame.vue"

Vue.use(VueRouter)

const routes: Array<RouteConfig> = [
    {
        path: "/",
        name: "home",
        redirect: { name: "games" },
    },
    {
        path: "/games/:gameId?",
        name: "games",
        component: BridgeGame,
    },
];

export default new VueRouter({
    mode: "history",
    base: process.env.BASE_URL,
    routes,
});
