from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool

import pytest

from .main import app
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


@pytest.fixture()
def redis_client(request):
    import fakeredis
    return fakeredis.FakeAsyncRedis()


def test_root_response():
    response = client.get("/")
    assert response.json() == {"message": "Hello Brave New World"}


@pytest.mark.asyncio
# Damn async databases
async def test_health_check(redis_client):
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
async def test_health_check_head(redis_client):
    response = client.head("/check/thisid")
    assert response.status_code == 200
