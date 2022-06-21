from unittest.mock import AsyncMock

from starlette.testclient import TestClient

from line_server.exceptions import IndexOutOfBounds
from line_server.redis.client import RedisClient
from line_server.server import app


def test_get_line_ok():
    mock_value = "hello world"

    mock_redis_client = AsyncMock(
        spec_set=RedisClient, **{"get_value.return_value": mock_value}
    )

    app.state.redis_client = mock_redis_client

    client = TestClient(app)

    response = client.get("/lines/1")
    response_body = response.json()

    assert response_body == mock_value
    assert response.status_code == 200


def test_get_line_bad_request():
    mock_redis_client = AsyncMock(
        spec_set=RedisClient, **{"get_value.side_effect": IndexOutOfBounds}
    )

    app.state.redis_client = mock_redis_client

    client = TestClient(app)

    response = client.get("/lines/99")

    assert response.status_code == 413
