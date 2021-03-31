from sqlalchemy import DATETIME, DateTime

from magnet.database import Base


def test_datetime_column_must_be_timezone_true():
    """sqlalchemyのdatetimeカラムはtimezone=Trueとなっていること"""
    datetimes = {}
    for table in Base.metadata.tables.values():
        # for column in table.columns.values():
        for column in table._columns._colset:  # sqlalchemy1.4
            if isinstance(column.type, DateTime):
                datetimes[table.name + "." + column.name] = column.type

    ignores = {"dummies.date_naive"}

    for name, dtype in datetimes.items():
        if name not in ignores:
            assert name and dtype.timezone == True
        else:
            assert name and dtype.timezone == False
