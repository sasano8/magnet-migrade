from libs.decorators import Tag

crawlers: Tag = Tag(tag="crawler", key_selector=lambda func: func.__name__)
