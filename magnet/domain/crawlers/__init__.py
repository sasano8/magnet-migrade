from libs.decorators import Tag


def setup(func):
    func()
    return func


@setup
def register_crawlers():
    """クローラを登録する"""
    from .crud import crawlers  # isort:skip
    from .impl import google
