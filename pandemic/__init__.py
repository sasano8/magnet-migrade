from .pandemic_fastapi import Unpack
from .pandemic_fastapi import create_fastapi as FastAPI
from .pandemic_fastapi import create_router as APIRouter
from .signaturebuilder import Adapters, SignatureBuilder

# TODO: pydantic analyzerはどこも参照していないので、pandemicにテストのみ移植する。
# TODO: BaseModel生成時、ModelField.inferでFieldInfoが生成されるので、それをもっと活用する
# TODO: 正規化する必要のないデフォルト値（QueryやFieldInfoなど）のスキップ処理を考える
# TODO: /app/libs/generator/__init__.py
# TODO: cli.db get_table_define_as_markdown
