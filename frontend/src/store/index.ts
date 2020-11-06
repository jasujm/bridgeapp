import Vue from "vue"
import Vuex from "vuex"
import { ActionContext as BaseActionContext } from "vuex"
import Api from "@/api"

Vue.use(Vuex);

export class State {
    username = "";
    api = new Api();
}

export type ActionContext = BaseActionContext<State, State>;

export const mutations = {
    updateUsername(state: State, username: string) {
        state.username = username;
    },
};

export const actions = {
    login(context: ActionContext, username: string) {
        if (username) {
            context.commit("updateUsername", username);
            context.state.api.authenticate(username);
        }
    }
};

export const getters = {
    isLoggedIn(state: State) {
        return Boolean(state.username);
    },
};

export default new Vuex.Store({
    state: new State(),
    mutations,
    actions,
    getters,
});
