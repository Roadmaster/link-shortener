from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_root_response():
    response = client.get("/")
    assert response.json() == {"message": "Hello Brave New World"}
