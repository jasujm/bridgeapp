<template>
  <ValidatedForm ref="createGameForm" :submitHandler="createGame">
    <ValidatedFormGroup
      name="Name"
      rules="required|min:2|max:63"
      v-slot="{ labelId, state }"
    >
      <b-form-input
        :id="labelId"
        :state="state"
        v-model="gameCreate.name"
        name="name"
      >
      </b-form-input>
    </ValidatedFormGroup>
    <b-form-group>
      <b-form-checkbox v-model="gameCreate.isPublic" name="isPublic">
        Public (displayed in search)
      </b-form-checkbox>
    </b-form-group>
    <b-button type="submit" variant="primary">Create</b-button>
  </ValidatedForm>
</template>

<script lang="ts">
import { Vue, Component, Ref } from "vue-property-decorator";
import ValidatedForm from "./ValidatedForm.vue";
import ValidatedFormGroup from "./ValidatedFormGroup.vue";
import { GameCreate } from "../api/types";

@Component({
  components: {
    ValidatedForm,
    ValidatedFormGroup,
  },
})
export default class CreateGameForm extends Vue {
  @Ref() private readonly createGameForm!: ValidatedForm;
  private gameCreate = new GameCreate();

  async createGame() {
    const api = this.$store.state.api;
    const game = await api.createGame(this.gameCreate);
    await api.joinGame(game.id);
    this.$emit("game-selected", game.id);
    this.gameCreate = new GameCreate();
    this.createGameForm.reset();
  }
}
</script>
