import { expect } from "./common"
import { State, ActionContext, mutations, actions, getters } from "@/store"
import { stubInterface } from "ts-sinon"
import sinon, { SinonStub } from "sinon"

describe("store", function() {
    let state: State;

    this.beforeEach(function() {
        state = new State();
    });

    it("should initially have no user logged in", function() {
        expect(getters.isLoggedIn(state)).to.be.false;
    });
    it("should update username when committing login", function() {
        mutations.updateUsername(state, "user");
        expect(state.username).to.be.equal("user");
    })
    it("should be logged in after committing login", function() {
        mutations.updateUsername(state, "user");
        expect(getters.isLoggedIn(state)).to.be.true;
    });

    describe("login action", function() {
        let context: ActionContext;
        let stubAuthenticate: SinonStub;

        this.beforeEach(function() {
            context = stubInterface<ActionContext>();
            context.state = state;
            stubAuthenticate = sinon.stub(state.api, "authenticate");
        });

        it("should update username", function() {
            actions.login(context, "user");
            expect(context.commit).to.be.calledWith("updateUsername", "user");
        });
        it("should authenticate API", function() {
            actions.login(context, "user");
            expect(stubAuthenticate).to.be.calledWith("user");
        });
        it("should not update when username is empty", function() {
            actions.login(context, "");
            expect(context.commit).not.to.be.called;
            expect(stubAuthenticate).not.to.be.called;
        });
    });
});
