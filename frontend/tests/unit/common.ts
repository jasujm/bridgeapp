import { createLocalVue } from "@vue/test-utils"
import { BootstrapVue } from "bootstrap-vue"
import Vuex from "vuex"
import chai from "chai"
import sinonChai from "sinon-chai"

export const localVue = (function() {
    const localVue = createLocalVue()
    localVue.use(BootstrapVue);
    localVue.use(Vuex)
    return localVue;
})();

export const expect = (function() {
    chai.use(sinonChai);
    return chai.expect;
})();
