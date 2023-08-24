from fastapi import FastAPI
import datetime
from . import database
from sqlalchemy import text

app = FastAPI()


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

