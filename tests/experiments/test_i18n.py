from devtools import debug
from pydantic import BaseModel, FilePath, ValidationError

"""
グローバライズするには、GNU gettextを用いることが多い。
python実装版が標準モジュールで提供されているので、利用することができる。

import gettext

要点
1. gettext: ソース中から多言語対応すべき文字列を抽出 (POT作成)
2. msginit: POTから各言語用に対訳ファイルを作成 (PO作成)
3. msgfmt: MOから対訳ファイルをバイナリ化 (MO作成)
"""


def test_pydantic_i18n():
    """pydanticのエラーメッセージをグローバライズする"""

    def localize(msg_id):
        """
        Very simple translation engine to demonstate,
        use gettext in real life with mo, po files etc.
        """
        translations = {
            "Value is not a valid float": "La valeur n'est pas un float valide",
            'Not a valid path: "{path}"': 'Chemin non valide: "{path}"',
        }
        try:
            return translations[msg_id]
        except TypeError as e:
            raise RuntimeError(f'no translations for "{msg_id}"') from e

    messages = {
        "type_error.float": localize("Value is not a valid float"),
        "value_error.path.not_exists": localize('Not a valid path: "{path}"'),
        # ... other translations
    }

    class Model(BaseModel):
        a: float
        p: FilePath

    try:
        Model(a="foo", p="/does/not/exist")
    except ValidationError as e:
        # raw errors:
        debug(e.errors())

        # errors again but translated:
        translated_errors = {}
        for error in e.errors():
            msg = messages[error["type"]]
            ctx = error.get("ctx")
            if ctx:
                msg = msg.format(**ctx)
            translated_errors[error["loc"][0]] = msg

        debug(translated_errors)
