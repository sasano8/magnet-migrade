from typing import Any, Dict


# TODO: どこで使ってるの？使ってる場所確認して、適切な場所へ移動する
def remove_none_value_from_dic(**kwargs: Dict[Any, Any]):
    removed = {k: v for k, v in kwargs.items() if v is not None}
    return removed


def create_params(__remove_none: bool = True, **kwargs) -> Dict[Any, Any]:
    if __remove_none:
        dic = remove_none_value_from_dic(**kwargs)
    else:
        dic = kwargs

    return dic
