import os
from typing import Any, Callable, Dict, Type, Union

from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.schemas import SchemaGenerator

from line_server.exceptions import IndexOutOfBounds, LineServerException
from line_server.redis.client import new_redis_client
from line_server.redis.exceptions import RedisError

load_dotenv()

FILE_NAME = "text.txt"
PORT = int(os.getenv("PORT", 8000))


schemas = SchemaGenerator(
    {
        "openapi": "3.0.0",
        "info": {"title": "line-server", "version": "1.0"},
    }
)


def openapi_schema(request: Request) -> Response:
    return schemas.OpenAPIResponse(request=request)


async def startup() -> None:
    redis_client = await new_redis_client()
    app.state.redis_client = redis_client

    await redis_client.add_to_data_store(FILE_NAME)

    print("Service started")


async def shutdown() -> None:
    await app.state.redis_client.close()
    print("Service shutdown")


async def get_line_handler(request: Request) -> Response:
    """
    responses:
        200:
            description: Get a line.
            examples: "line text"
    """

    line_index = request.path_params["line_index"]
    line = await app.state.redis_client.get_value(line_index)

    return JSONResponse(line, status_code=200)


def server_error_handler(request: Request, exc: Exception) -> Response:
    """Handles internal server error."""

    return Response(str(exc), status_code=500)


def index_out_of_bounds_handler(
    request: Request, exc: LineServerException
) -> Response:
    """Handles when a line request is beyond the end of the file."""
    return Response(status_code=413)


routes = [
    Route("/", openapi_schema, methods=["GET"], include_in_schema=False),
    Route("/lines/{line_index:int}", get_line_handler, methods=["GET"]),
]

exception_handlers: Dict[Union[int, Type[Exception]], Callable[..., Any]] = {
    RedisError: server_error_handler,
    IndexOutOfBounds: index_out_of_bounds_handler,
}


app = Starlette(
    debug=True,
    routes=routes,
    on_startup=[startup],
    on_shutdown=[shutdown],
    exception_handlers=exception_handlers,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
    )
