# TODO: 使ってないなら消す

from graphlib import TopologicalSorter

from pydantic import BaseModel, Field
from pydantic.typing import Literal

# from libs.linq import Linq


# class Job(BaseModel):
#     name: str = Field(..., readOnly=True)
#     depends: list[Job] = []
#     status: Literal["not_running", "running", "success", "abort"] = "not_running"
#     pending: bool = False

#     @property
#     def is_not_run(self):
#         s = self.status
#         if s == "not_running":
#             return True
#         elif s == "running":
#             return True
#         elif s == "success":
#             return False
#         elif s == "abort":
#             return False
#         else:
#             raise Exception()


# class Dag(BaseModel):
#     __root__: list[Job]
#     _nodes: dict[str, Job] = {}

#     def get_all(self):
#         return Linq(self.__root__).select_recursive(lambda x: x.depends).distinct()

#     def get_ready(self):
#         ts = TopologicalSorter()
#         nodes = (
#             self.get_all()
#             .filter(lambda x: x == "not_running")
#             .to_dict(lambda x: x.name)
#         )

#         for node in nodes.values():
#             depends = (
#                 Linq(node.depends)
#                 .filter(lambda x: not x == "success")
#                 .map(lambda x: x.name)
#                 .to_list()
#             )
#             ts.add(node.name, *depends)

#         return Linq(ts.static_order()).map(lambda x: nodes[x]).save()
