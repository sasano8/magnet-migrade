import asyncio

from framework.workers import RecursiveFunctionAsync


def test_recursive_async():
    history = []

    @RecursiveFunctionAsync
    async def sample(state):
        """メッセージキューから実行する関数と引数情報を受信し、関数を非同期に実行する"""
        state.is_cancelled = False
        return state

    # 使ってない
    @sample.on_cancel
    def cancel(state):
        assert state.is_cancelled

    # エントリーポイント
    @sample.on_main
    async def startup(state):
        return step_first

    @sample.on_step
    async def shutdown(state):
        ...

    @sample.on_step
    async def step_first(state):
        if state.is_cancelled:
            return shutdown

        history.append(1)

        return loop_two

    @sample.on_step
    async def loop_two(state):
        if state.is_cancelled:
            return shutdown

        if len(history) == 0:
            raise Exception()
        elif len(history) == 1:
            history.append(2)
            return loop_two
        elif len(history) == 2:
            history.append(3)
            return loop_two

        return shutdown

    class State:
        pass

    asyncio.run(sample(State()))
    assert history == [1, 2, 3]
