import tracemalloc

from .views import router

cache_size = 0


# @router.on_event("startup")
# def start_statistics():
#     tracemalloc.start()


def get_statistics():
    global cache_size

    snapshot = tracemalloc.take_snapshot()
    stats = snapshot.statistics("lineno")

    total_size = sum(map(lambda x: x.size, stats)) / 1000
    str_stats = [str(x) for x in stats]
    diff_size = total_size - cache_size
    cache_size = total_size

    return diff_size, total_size, str_stats
