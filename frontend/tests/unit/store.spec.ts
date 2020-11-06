import { expect } from "./common"
import { ActionContext, mutations, actions, getters } from "@/store"
import { stubInterface } from "ts-sinon"

describe("store", function() {
    it("should initially have no user logged in", function() {
        const state = { username: null };
        expect(getters.isLoggedIn(state)).to.be.false;
    });
    it("should update username when committing login", function() {
        const state = { username: null };
        mutations.updateUsername(state, "user");
        expect(state.username).to.be.equal("user");
        expect(getters.isLoggedIn(state)).to.be.true;
    })
    it("should login user when dispatching login action", function() {
        const context = stubInterface<ActionContext>()
        actions.login(context, "user");
        expect(context.commit).to.be.calledWith("updateUsername", "user");
    });
    it("should not login user when username is empty", function() {
        const context = stubInterface<ActionContext>()
        actions.login(context, "");
        expect(context.commit).not.to.be.called;
    });
});
