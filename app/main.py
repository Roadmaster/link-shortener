from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello Brave New World"}


@app.get("/check/{check_id}")
async def health_check(check_id: str):
    import datetime
    time = datetime.datetime.now()
    return f"App is healthy: {time}"

