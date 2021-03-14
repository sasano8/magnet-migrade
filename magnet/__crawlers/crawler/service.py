from . import crud
from magnet.database import Session
from .driverpool import get_driver_manager
from magnet.executor import service as executor
from magnet.ingester import schemas as ingester

# クローラはアノテーションによりが登録されるためモジュールを呼び出すこと
from . import impl


def get_crawler_func_by_name(crawler_name: str):
    func = crud.crawlers.get(crawler_name)
    return func


def exec_job(job: ingester.TaskCreate):
    driver_manager = get_driver_manager()
    driver = driver_manager.driver

    data = job.dict()
    input = ingester.CommonSchema(**data)

    from magnet.database import get_db

    it = get_db()
    db = next(it)
    
    obj = executor.instatiate_executor(input, db=db)

    try:
        for item in obj.crawler(driver, input):
            item.sync_summary_from_detail()
            obj(item)

    except Exception as e:
        raise

    finally:

        if driver is None:
            return

        # driverを再利用するため、１つだけタブを残して、それ以外のタブを全て閉じ、空白ページを表示させる
        driver_manager.cleanup_driver()

    return {"message": "Hello World"}

