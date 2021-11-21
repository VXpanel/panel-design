try:
    import sqlite3

    db = sqlite3.connect('database.db')
    sql = db.cursor()

    logs = """
    CREATE TABLE "servers" (
        "id"	INTEGER NOT NULL UNIQUE,
        "name"	TEXT,
        "ports"	TEXT,
        "password"	TEXT,
        PRIMARY KEY("id")
    );
    """

    sql.execute(logs)

    db.commit()
except:
    pass

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Нет базы данных")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f'Подключение к базе данных по адресу {conn_str}')

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()

class Server(SqlAlchemyBase):
    __tablename__ = 'servers'

    id = sa.Column(sa.Integer,
                   primary_key=True)
    name = sa.Column(sa.String, nullable=True)
    ports = sa.Column(sa.String, nullable=True)
    password = sa.Column(sa.String, nullable=True)