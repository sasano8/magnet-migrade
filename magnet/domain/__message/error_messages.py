from enum import IntEnum


class RFC7807:
    status: str = "サーバによって生成されたHTTPステータスコード"
    type: str = "エラーの詳細ドキュメントへのURL"
    title: str = "人間が読むためのサマリー"
    detail: str = "人間が読むことのできる説明文"
    instance: str = "問題発生箇所の参照URI"

    # アプリケーション固有フィールド
    errors: list

    def __init__(self, status, type, title, detail, instance, errors):
        if type is SystemError:
            pass
        elif type is ValueError:
            pass
        else:
            pass


class ErrorCode(IntEnum):
    """
    - S: システムエラー
    - A: アプリケーションエラー
    - V: 検証エラー
    """

    S_INTERNAL_SERVER_ERROR = 1
    A_FAILURE_LOGIN = 100
    V_DUPULICATE = 1000


messages_en = {
    ErrorCode.S_INTERNAL_SERVER_ERROR: "システムエラーが発生しました。",
    ErrorCode.A_FAILURE_LOGIN: "ログインに失敗しました。",
}

messages_jp = {
    ErrorCode.S_INTERNAL_SERVER_ERROR: dict(exc=SystemError, msg="システムエラーが発生しました。"),
    ErrorCode.A_FAILURE_LOGIN: dict(exc=SystemError, msg="ログインに失敗しました。"),
}


standard_error_mapper = [
    dict(type=ValueError, status=422, title="処理要求時に検証エラーが発生しました。"),
    # 滑り止め
    dict(type=SystemError, status=500, title="処理要求時に想定外のシステムエラーが発生しました。"),
    dict(type=Exception, status=500, title="処理要求時に想定外のシステムエラーが発生しました。"),
]


def mapping_error(e):
    dic = {x["type"]: x for x in standard_error_mapper}
    e_info = dic.get(e.__class__)
    if e_info is None:
        return None

    status = e_info["status"]
    title = e_info["title"]

    return RFC7807(status=status, type=e.__class__, title=title, detail=str(e))
