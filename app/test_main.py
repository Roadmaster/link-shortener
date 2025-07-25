from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool

import pytest

from .main import app, get_redis
from . import database

client = TestClient(app)

test_engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    echo=False,
    poolclass=StaticPool,
)


@pytest.fixture()
async def test_db():
    await database.initdb(test_engine)


def redis_client():
    import fakeredis
    return fakeredis.FakeAsyncRedis()


app.dependency_overrides[get_redis] = redis_client


def test_root_response():
    response = client.get("/")
    assert response.json() == {"message": "Actually, link shorteners are evil"}


@pytest.mark.asyncio
# Damn async databases
async def test_health_check():
    response = client.get("/check/thisid")
    assert "App is healthy: " in response.text

    await database.initdb(database.engine)
    async with database.engine.connect() as conn:
        result = await conn.execute(
            text("SELECT count(*) as ct FROM accesses WHERE name='thisid' ")
        )
        row = result.first()
        assert row.ct >= 1  # This test is bogus right now


@pytest.mark.asyncio
async def test_health_check_head():
    response = client.head("/check/thisid")
    assert response.status_code == 200
