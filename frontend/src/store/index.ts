import Vue from "vue";
import Vuex from "vuex";
import { ActionContext as BaseActionContext } from "vuex";
import Api from "@/api";
import { getErrorMessage, BasicAuth } from "@/api";
import { ErrorMessage } from "@/api/types";

Vue.use(Vuex);

export class State {
  isLoggedIn = false;
  api = new Api();
  error = new ErrorMessage();
}

export type ActionContext = BaseActionContext<State, State>;

export const mutations = {
  setError(state: State, error: ErrorMessage) {
    state.error = error;
  },
};

export const actions = {
  async login(context: ActionContext, auth: BasicAuth) {
    if (auth) {
      const success = await context.state.api.authenticate(auth);
      if (success) {
        context.state.isLoggedIn = true;
      }
    }
  },
  logout(context: ActionContext) {
    context.state.api.forgetAuth();
    context.state.isLoggedIn = false;
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
    return state.isLoggedIn;
  },
};

export default new Vuex.Store({
  state: new State(),
  mutations,
  actions,
  getters,
});
