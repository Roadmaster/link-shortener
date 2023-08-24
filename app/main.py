import datetime

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from . import database

app = FastAPI()
Instrumentator().instrument(app).expose(app)


@app.get("/")
async def root():
    return {"message": "Hello Brave New World"}


@app.get("/check/{check_id}")
async def health_check(check_id: str):
    await database.initdb(database.engine)
    time = datetime.datetime.now()
    async with database.engine.connect() as conn:
        # Write a record
        await database.write_record(conn=conn, check_id=check_id, time=time)

    return f"App is healthy: {time}"

