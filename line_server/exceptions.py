class LineServerException(Exception):
    pass


class IndexOutOfBounds(LineServerException):
    pass


class RedisConnectionError(LineServerException):
    pass
