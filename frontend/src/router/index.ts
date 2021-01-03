import Vue from 'vue'
import VueRouter, { RouteConfig } from "vue-router"
import BridgeGame from "../views/BridgeGame.vue"
import NotFound from "../views/NotFound.vue"

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
    {
        path: "*",
        component: NotFound,
    },
];

export default new VueRouter({
    mode: "history",
    base: process.env.BASE_URL,
    routes,
});
