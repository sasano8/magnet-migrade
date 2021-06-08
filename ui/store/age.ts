import { getterTree, mutationTree, actionTree } from "typed-vuex";

export const state = () => ({
  age: 0 as number,
});

export type RootState = ReturnType<typeof state>;

export const getters = getterTree(state, {
  age: (state) => state.age,
});

export const mutations = mutationTree(state, {
  setAge(state, age: number): void {
    state.age = age;
  },
});

export const actions = actionTree(
  { state, getters, mutations },
  {
    getOlder({ getters, commit }) {
      const currentAge = getters.age;
      commit("setAge", currentAge + 1);
    },
    hoge(): string {
      return "i am hoge";
    },
    fuga({ dispatch }) {
      const res = dispatch("hoge");
    },
  }
);
