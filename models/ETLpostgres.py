import sqlalchemy  # type: ignore
from repo.config import database_config, database_url
import pandas  # type: ignore
import os

user, pswd, host, port, name, _ = database_config()


def load_data(filename: str):
    path = os.path.join(os.path.dirname(__file__), filename)

    if filename[-3:] == ".h5":
        return pandas.read_hdf(path)

    return pandas.read_csv(path)


def to_postgres(filepath, tablename, if_exists="append"):
    engine = sqlalchemy.create_engine(database_url())  # connect to server
    df = load_data(filepath)
    df.to_sql(tablename, engine, if_exists=if_exists, index=False)


def from_postgres(tablename):
    engine = sqlalchemy.create_engine(database_url())  # connect to server
    if not engine.dialect.has_table(engine, tablename):
        return None
    return pandas.read_sql_query("select * from public.{}".format(tablename), engine)


def test_etl_postgres():
    to_postgres("../Simulation_engine/dummy_data_useful.h5", "data_test")
    df = from_postgres("data_test")
    df2 = load_data("../Simulation_engine/dummy_data_useful.h5")
    print(df.dtypes)
    print(df2.dtypes)
    df.to_csv("mouline.csv")
    df2.to_csv("nonmouline.csv")
    df.to_hdf("dummy_data_useful_hachee.h5", key="input")
    for k in df.columns:
        print(
            k,
            len(df[df[k] != df2[k]]),
            (len(df[(df[k] - df2[k]) < -0.001]) + len(df[(df[k] - df2[k]) > 0.001]))
            if len(df[df[k] != df2[k]])
            else "",
        )
