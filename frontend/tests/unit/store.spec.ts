import { expect } from "./common"
import { State, ActionContext, mutations, actions, getters } from "@/store"
import { ErrorMessage } from "@/api/types"
import * as api from "@/api"
import { stubInterface } from "ts-sinon"
import sinon, { SinonStub } from "sinon"

const auth = { username: "user", password: "secret" };

describe("store", function() {
    let state: State;
    let context: ActionContext;

    this.beforeEach(function() {
        state = new State();
        context = stubInterface<ActionContext>();
        context.state = state;
    });

    it("should set error", function() {
        const error = new ErrorMessage("error");
        mutations.setError(state, error);
        expect(state.error).to.be.equal(error);
    });

    it("should initially have no user logged in", function() {
        expect(getters.isLoggedIn(state)).to.be.false;
    });

    describe("login action", function() {
        let stubAuthenticate: SinonStub;

        this.beforeEach(function() {
            stubAuthenticate = sinon.stub(state.api, "authenticate").resolves(true);
        });

        this.afterEach(function() {
            stubAuthenticate.restore();
        });

        it("should authenticate API", async function() {
            await actions.login(context, auth);
            expect(stubAuthenticate).to.be.calledWith(auth);
        });

        it("should update the logged in status on success", async function() {
            await actions.login(context, auth);
            expect(getters.isLoggedIn(state)).to.be.true;
        });

        it("should not update the logged in status on failure", async function() {
            stubAuthenticate.resolves(false);
            await actions.login(context, auth);
            expect(getters.isLoggedIn(state)).to.be.false;
        });
    });

    describe("logout action", function() {
        let stubForgetAuth: SinonStub;

        this.beforeEach(function() {
            state.isLoggedIn = true;
            stubForgetAuth = sinon.stub(state.api, "forgetAuth");
        });

        this.afterEach(function() {
            stubForgetAuth.restore();
        });

        it("should forget auth credentials", async function() {
            await actions.logout(context);
            expect(stubForgetAuth).to.be.called;
        });

        it("should update the logged in status", async function() {
            await actions.logout(context);
            expect(getters.isLoggedIn(state)).to.be.false;
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
