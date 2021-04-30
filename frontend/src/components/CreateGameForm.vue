<template>
  <ValidatedForm ref="createGameForm" :submitHandler="createGame">
    <ValidatedFormGroup
      name="Name"
      rules="required|min:2|max:63"
      v-slot="{ labelId, state }"
      no-label
    >
      <b-input-group>
        <b-form-input
          :id="labelId"
          :state="state"
          placeholder="Name"
          v-model="name"
          name="name"
        >
        </b-form-input>
        <b-button type="submit" variant="primary">Create</b-button>
      </b-input-group>
    </ValidatedFormGroup>
  </ValidatedForm>
</template>

<script lang="ts">
import { Vue, Component, Ref } from "vue-property-decorator";
import ValidatedForm from "./ValidatedForm.vue";
import ValidatedFormGroup from "./ValidatedFormGroup.vue";

@Component({
  components: {
    ValidatedForm,
    ValidatedFormGroup,
  },
})
export default class CreateGameForm extends Vue {
  @Ref() private readonly createGameForm!: ValidatedForm;
  private name = "";

  async createGame() {
    const api = this.$store.state.api;
    const game = await api.createGame(this.name);
    await api.joinGame(game.id);
    this.$emit("game-selected", game.id);
    this.name = "";
    this.createGameForm.reset();
  }
}
</script>
