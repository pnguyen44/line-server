import pytest

from line_server.exceptions import IndexOutOfBounds
from line_server.redis.client import new_redis_client

FILE_NAME = "text.txt"


@pytest.mark.asyncio
async def test_write_and_read():
    redis = await new_redis_client()
    await redis.add_to_data_store(FILE_NAME)

    keys = await redis.get_keys()
    assert len(keys) == 92

    assert (
        await redis.get_value("1")
        == "Covid is making flu and other common viruses act in unfamiliar ways Doctors are rethinking routines, including keeping preventive shots on hand into the spring and even summer."
    )

    assert (
        await redis.get_value("92")
        == "“We need to carry some of the lessons we learned forward,” Foxman said."
    )

    with pytest.raises(IndexOutOfBounds):
        await redis.get_value("99")
