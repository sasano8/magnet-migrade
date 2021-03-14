from typing import List

import hjson
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from libs import generator

router = InferringRouter()


@cbv(router)
class DevelopView:
    @router.post("/test_request", response_class=HTMLResponse)
    def test_request(self):
        import requests

        res = requests.get("https://example.com/")
        return res.text

    # @router.post("/pytest", response_class=PlainTextResponse)
    # def exec_pytest(self, module: str = None):
    #     from main import exec_pytest
    #     result = exec_pytest(module)
    #     return result

    @router.post("/json_to_pydantic", response_class=PlainTextResponse)
    async def json_to_pydantic(self, json: str = "{}"):
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
