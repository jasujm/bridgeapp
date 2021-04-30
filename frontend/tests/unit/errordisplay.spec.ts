import { localVue, expect } from "./common";
import { mount, Wrapper } from "@vue/test-utils";
import ErrorDisplay from "@/components/ErrorDisplay.vue";
import { ErrorSeverity } from "@/api/types";
import _ from "lodash";

describe("ErrorDisplay.vue", function () {
  let wrapper: Wrapper<ErrorDisplay>;

  this.beforeEach(function () {
    wrapper = mount(ErrorDisplay, { localVue });
  });

  it("should display error message", async function () {
    wrapper.setProps({ message: "message" });
    await wrapper.vm.$nextTick();
    expect(wrapper.find(".alert").text()).to.contain("message");
  });

  for (const severity of _.values(ErrorSeverity)) {
    it(`should support severity ${severity}`, async function () {
      wrapper.setProps({ message: "message", severity });
      await wrapper.vm.$nextTick();
      expect(wrapper.find(".alert").classes()).to.include(`alert-${severity}`);
    });
  }
});
