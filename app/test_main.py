from fastapi.testclient import TestClient
from sqlalchemy import text
import pytest

from .main import app
from . import database

client = TestClient(app)


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_root_response():
    response = client.get("/")
    assert response.json() == {"message": "Hello Brave New World"}


@pytest.mark.asyncio
# Damn async databases
async def test_health_check():
    response = client.get("/check/thisid")
    assert "App is healthy: " in response.text

    database.initdb(database.engine)
    async with database.engine.connect() as conn:
        result = await conn.execute(
            text("SELECT count(*) as ct FROM accesses WHERE name='thisid' ")
        )
        row = result.first()
        assert row.ct >= 1  # This test is bogus right now
