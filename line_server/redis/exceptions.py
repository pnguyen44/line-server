class RedisError(Exception):
    """Base class from Redis exception."""

    pass


class RedisConnectionError(RedisError):
    """Raised when failed to connect to Redis."""

    pass
