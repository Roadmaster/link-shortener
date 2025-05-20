import datetime
import logging
import random

from fastapi import Depends, FastAPI, HTTPException

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Summary, Counter

import redis.asyncio as redis

from . import database

logger = logging.getLogger(__name__)

app = FastAPI()
Instrumentator().instrument(app).expose(app)

class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        if " /metrics " in message or " /health " in message:
            return False
        if " /check/healthy " in message or " /check " in message:
            return False
        return True


# Filter out /endpoint
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

g = Summary("redis_response_time_seconds", "Redis response time")
rce = Counter("redis_connection_errors_count", "Redis connection errors")


@app.get("/")
async def root():
    return {"message": "Hello Brave New World! "}


async def get_redis():
    pool = database.redis_pool
    return await redis.Redis(connection_pool=pool)


@app.get("/check/{check_id}")
@app.head("/check/{check_id}")
async def health_check(check_id: str, redis_client=Depends(get_redis)):
    logger.info("Getting health check")
    #    logger.debug("This is a debug message")
    await database.initdb(database.engine)
    fail = False
    if fail:
        # reset fail in the db
        raise HTTPException(status_code=500, detail="Database error sqlite")

    time = datetime.datetime.now()
    async with database.engine.connect() as conn:
        # Write a record
        # logger.error("Don't panic, everything is ok")
        await database.write_record(conn=conn, check_id=check_id, time=time)
    with g.time():
        expiry = random.randint(2500, 4000)
        try:
            ctr_value = await redis_client.incr("counter")
            await redis_client.set("last_write", str(time))
            await redis_client.set(str(time), "yipie", ex=expiry)
            lwrite = await redis_client.get("last_write")
            await redis_client.aclose()
        except Exception as bare:
            rce.inc()
            logger.exception(bare)
            raise HTTPException(status_code=500, detail="Database error redis")

    return f"App is healthy: {time} last write {lwrite} counter {ctr_value}"


# Add one endpoint
# make_health_fail writes a health_fail=True record to the db
# if health_fail is true in the db, then health_check returns a 500 error
# and resets the make-health_fail thing
#
#


@app.get("/oom")
async def oom():
    listy = ["a" for _ in range(1000000 * 256)]
    return "oom attempt"
