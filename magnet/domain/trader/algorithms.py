from typing import Callable

from framework import MiniDB


class DetectorRepository(MiniDB[Callable]):
    pass


detectors = DetectorRepository()


def montecalro():
    # https://note.com/mucun_wuxian/n/n91bb098abfcf
    pass


def build_detector_code(func_name, script, invert_ask_or_bid: bool = False):
    global_namespace = {}
    local_namespace = {}

    header = f"def {func_name}(topic):"
    code = "\n".join([header, script])

    # TODO: 脆弱性あり。ハックを防ぐために、サンドボックス環境にしたい。
    # 完全にサンドボックスを保証することは難しいが、悪意あるコードを実行しそうなコードを監視する
    # importを除く __FILE__を除く
    exec(code, global_namespace, local_namespace)
    func = local_namespace[func_name]
    if invert_ask_or_bid:
        func = wrap_func_with_invert_ask_or_bid(func)
    return func


def wrap_func_with_invert_ask_or_bid(func):
    def invert_func(topic):
        result = func(topic)
        if result == "ask":
            return "bid"
        elif result == "bid":
            return "ask"
        else:
            return result

    return invert_func


@detectors.add
def detect_t_cross(ticker):
    # サイン検出
    if ticker.t_cross == 0:
        return None
    elif ticker.t_cross == 1:
        return "ask"
    elif ticker.t_cross == -1:
        return "bid"
    else:
        raise Exception()


@detectors.add
def detect_t_cross_invert(ticker):
    # サイン検出
    if ticker.t_cross == 0:
        return None
    elif ticker.t_cross == -1:
        return "ask"
    elif ticker.t_cross == 1:
        return "bid"
    else:
        raise Exception()
