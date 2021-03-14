

# publish query parameter
FastAPIはBaseModelをリクエストボディとして認識しますが、クエリパラメータ群と認識させる方法を提供していません。
pandemicは、BaseModelのフィールドをクエリパラメータと公開させることができます。

それを利用するには次のようにします。

1. Unpackを継承したBaseModelクラスを作成する。
2. BaseModel.Config.allow_population_by_field_name = True を設定する。（エイリアスによりパラメータを受け入れるために必要です）
3. それを引数の型として設定します。

``` python
from pydantic import BaseModel
from fastapi import Query
import pandemic

class QCommon(BaseModel, pandemic.Unpack):
    skip: int = Query(0, ge=0)
    limit: int = Query(100, ge=0)

    class Config:
        allow_population_by_field_name = True

app = pandemic.FastAPI()


@app.get("/")
def get_data(query: QCommon):
    return query

```

リクエストボディとクエリパラメータの区別をつけるため、クラス名は接頭語などで特別な意図があることを示すのがいいでしょう。（例えば、Q)
また、デメリットとして元の関数へバインド処理を行うため、オーバーヘッドが生じことに注意してください。

# pydantic based view
pandemicはpydantic based viewを提供します。
BaseModelにデコレータを付与すると、__call__をエンドポイントとして公開します。

``` python
from pydantic import BaseModel
import pandemic

app = pandemic.FastAPI()

@app.get("/hello")
class HelloUser(BaseModel):
    name: str = Field("test", description="名前を入力してください")

    async def __call__(self):
        return self
```




# adapter
pandemicのコア機能は、関数やクラスの型注釈を利用した新たなコーディングスタイルを開拓することです。
Adaptersに定義されているアダプタを利用して、型注釈を活用する周辺ライブラリと連携することができます。

``` python
import typer

from pydantic import BaseModel
import pandemic

app = typer.Typer()
to_typer = pandemic.SignatureBuilder.unpack_arguments(pandemic.Adapters.to_typer, prompt=True)


class CreateConfig(BaseSettings):
    db_host: str

@app.command()
@to_typer
def create_config(input: CreateConfig) -> None:
    ...
```
