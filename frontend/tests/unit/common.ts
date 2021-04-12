import { createLocalVue } from "@vue/test-utils"
import { BootstrapVue } from "bootstrap-vue"
import Vuex from "vuex"
import UniqueId from "vue-unique-id"
import chai from "chai"
import sinonChai from "sinon-chai"

export const localVue = (function() {
    const localVue = createLocalVue()
    localVue.use(BootstrapVue);
    localVue.use(Vuex)
    localVue.use(UniqueId)
    return localVue;
})();

export const expect = (function() {
    chai.use(sinonChai);
    return chai.expect;
})();
