import Vue from "vue"
import App from "./App.vue"
import store from "./store"
import router from "./router"
import { BootstrapVue } from "bootstrap-vue"

Vue.config.productionTip = false
Vue.config.errorHandler = function(err, vm) {
    vm.$store.dispatch("reportError", err);
};

import "bootstrap/dist/css/bootstrap.css"
import "bootstrap-vue/dist/bootstrap-vue.css"

Vue.use(BootstrapVue)

new Vue({
    store,
    router,
    render: h => h(App)
}).$mount("#app")
