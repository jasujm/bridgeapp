import Vue from "vue"
import Vuex from "vuex"
import { ActionContext as BaseActionContext } from "vuex"
import Api from "@/api"
import { getErrorMessage } from "@/api"
import { ErrorMessage } from "@/api/types"

Vue.use(Vuex);

export class State {
    username = "";
    api = new Api();
    error = new ErrorMessage();
}

export type ActionContext = BaseActionContext<State, State>;

export const mutations = {
    updateUsername(state: State, username: string) {
        state.username = username;
    },
    setError(state: State, error: ErrorMessage) {
        state.error = error;
    }
};

export const actions = {
    login(context: ActionContext, username: string) {
        if (username) {
            context.commit("updateUsername", username);
            context.state.api.authenticate(username);
        }
    },
    reportError(context: ActionContext, err: Error) {
        const error = getErrorMessage(err);
        if (error) {
            context.commit("setError", error);
        }
    },
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
