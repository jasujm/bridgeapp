import { expect } from "./common"
import { State, ActionContext, mutations, actions, getters } from "@/store"
import { ErrorMessage } from "@/api/types"
import * as api from "@/api"
import { stubInterface } from "ts-sinon"
import sinon, { SinonStub } from "sinon"

describe("store", function() {
    let state: State;
    let context: ActionContext;

    this.beforeEach(function() {
        state = new State();
        context = stubInterface<ActionContext>();
        context.state = state;
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

    it("should set error", function() {
        const error = new ErrorMessage("error");
        mutations.setError(state, error);
        expect(state.error).to.be.equal(error);
    });

    describe("login action", function() {
        let stubAuthenticate: SinonStub;

        this.beforeEach(function() {
            stubAuthenticate = sinon.stub(state.api, "authenticate");
        });

        this.afterEach(function() {
            stubAuthenticate.restore();
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

    describe("report error action", function() {
        const error = new Error();
        let stubReportError: SinonStub;

        this.beforeEach(function() {
            stubReportError = sinon.stub(api, "getErrorMessage");
        });

        this.afterEach(function() {
            stubReportError.restore();
        });

        it("should not do anything on null", function() {
            stubReportError.returns(null);
            actions.reportError(context, error);
            expect(stubReportError).to.be.calledWith(error);
            expect(context.commit).not.to.be.called;
        });
        it("should not do anything on null", function() {
            const errorMessage = new ErrorMessage("error");
            stubReportError.returns(errorMessage);
            actions.reportError(context, error);
            expect(stubReportError).to.be.calledWith(error);
            expect(context.commit).to.be.calledWith("setError", errorMessage);
        });
    });
});
