import os


from sqlalchemy import Column
from sqlalchemy import MetaData
from sqlalchemy import select
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Table
from sqlalchemy import DateTime


from sqlalchemy.ext.asyncio import create_async_engine


meta = MetaData()
accesses = Table(
    "accesses",
    meta,
    Column("id", Integer, primary_key=True),
    Column("timestamp", DateTime),
    Column("name", String(50)),
)

SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL", "sqlite+aiosqlite:////tmp/ls.sqlite"
)

connect_args = {}
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    connect_args["check_same_thread"] = False
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace(
        "postgres://", "postgresql+asyncpg://"
    ).replace("sslmode", "ssl")


async def initdb(enginee):
    async with enginee.begin() as conn:
        await conn.run_sync(meta.create_all)


async def write_record(conn, check_id, time):
    await conn.execute(accesses.insert(), [{"name": check_id, "timestamp": time}])
    await conn.commit()


engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=1800,
)
