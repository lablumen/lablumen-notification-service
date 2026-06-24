from fastapi.testclient import TestClient

from app.main import app

# Instantiated without a context manager so the SQS consumer lifespan does not start during tests.
client = TestClient(app)


def test_healthz_ok():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
