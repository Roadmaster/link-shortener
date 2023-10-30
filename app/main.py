import datetime

from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator


from . import database

app = FastAPI()
Instrumentator().instrument(app).expose(app)


@app.get("/")
async def root():
    return {"message": "Hello Brave New World"}


@app.get("/check/{check_id}")
@app.head("/check/{check_id}")
async def health_check(check_id: str):
    await database.initdb(database.engine)
    fail = False
    if fail:
        # reset fail in the db
        raise HTTPException(status_code=500, detail="I'm so flakey")

    time = datetime.datetime.now()
    async with database.engine.connect() as conn:
        # Write a record
        await database.write_record(conn=conn, check_id=check_id, time=time)

    return f"App is healthy: {time}"


# Add one endpoint
# make_health_fail writes a health_fail=True record to the db
# if health_fail is true in the db, then health_check returns a 500 error
# and resets the make-health_fail thing
#
#
