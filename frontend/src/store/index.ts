import Vue from "vue"
import Vuex from "vuex"
import { ActionContext as BaseActionContext } from "vuex"

Vue.use(Vuex);

export class State {
    username: string | null = null;
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
        }
    }
};

export const getters = {
    isLoggedIn(state: State) {
        return state.username != null;
    },
};

export default new Vuex.Store({
    state: new State(),
    mutations,
    actions,
    getters,
});
