def remove_none_value_from_dic(**kwargs: dict):
    removed = {k: v for k, v in kwargs.items() if v is not None}
    return removed


def create_params(__remove_none: bool = True, **kwargs) -> dict:
    if __remove_none:
        dic = remove_none_value_from_dic(**kwargs)
    else:
        dic = kwargs

    return dic
