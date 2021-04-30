import { expect } from "./common";
import { getErrorMessage } from "@/api";
import { ErrorSeverity } from "@/api/types";
import { AxiosError, AxiosResponse } from "axios";
import { stubInterface } from "ts-sinon";

describe("api", function () {
  describe("getErrorMessage", function () {
    let error: AxiosError;
    let response: AxiosResponse;

    this.beforeEach(function () {
      error = stubInterface<AxiosError>();
      response = stubInterface<AxiosResponse>();
      error.response = response;
    });

    it("should return null if the error is not axios error", function () {
      expect(getErrorMessage(new Error())).to.be.null;
    });
    it("should return if there is no response", function () {
      error.isAxiosError = true;
      const errorMessage = getErrorMessage(error);
      expect(errorMessage)
        .to.have.property("severity")
        .that.is.equal(ErrorSeverity.danger);
    });
    it("should return generic error on error response without detail", function () {
      error.isAxiosError = true;
      response.status = 500;
      const errorMessage = getErrorMessage(error);
      expect(errorMessage)
        .to.have.property("severity")
        .that.is.equal(ErrorSeverity.danger);
    });
    it("should return error detail in message", function () {
      error.isAxiosError = true;
      response.status = 400;
      response.data.detail = "message";
      const errorMessage = getErrorMessage(error);
      expect(errorMessage)
        .to.have.property("severity")
        .that.is.equal(ErrorSeverity.danger);
      expect(errorMessage).to.have.property("message").that.is.equal("message");
    });
    for (const status of [404, 409]) {
      it(`should return warning on ${status}`, function () {
        error.isAxiosError = true;
        response.status = status;
        response.data.detail = "warning";
        const errorMessage = getErrorMessage(error);
        expect(errorMessage)
          .to.have.property("severity")
          .that.is.equal(ErrorSeverity.warning);
        expect(errorMessage)
          .to.have.property("message")
          .that.is.equal("warning");
      });
    }
  });
});
