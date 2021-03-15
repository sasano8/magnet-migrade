import hjson
from fastapi.responses import PlainTextResponse

from libs import generator
from pandemic import APIRouter

router = APIRouter()


@router.post("/json_to_pydantic", response_class=PlainTextResponse)
async def json_to_pydantic(json: str = "{}"):
    dic = hjson.loads(json)

    model_name = "Dummy"
    code = generator.dump_pydantic_code_from_json(
        __model_name=model_name,
        data=dic,
        indent=4,
        require_default=False,
        set_default_from_json=False,
    )
    return code
