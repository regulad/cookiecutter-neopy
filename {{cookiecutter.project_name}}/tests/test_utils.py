import asyncio
import base64
import logging
import tracemalloc
from time import sleep
from typing import Literal
from typing import cast

import pytest

from {{cookiecutter.package_name}}.utils.asyncio import make_async
from {{cookiecutter.package_name}}.utils.asyncio import make_sync
from {{cookiecutter.package_name}}.utils.logging import add_remote_logger
from {{cookiecutter.package_name}}.utils.logging import configure_rich_logger
from {{cookiecutter.package_name}}.utils.logging import get_log_level
from {{cookiecutter.package_name}}.utils.messagepack import pack_messagepack
from {{cookiecutter.package_name}}.utils.messagepack import unpack_messagepack
from {{cookiecutter.package_name}}.utils.profiling import prepare_profiler
from {{cookiecutter.package_name}}.utils.timezone import timezone_aware_now


class TestTimezone:
    def test_timezone(self) -> None:
        utctime = timezone_aware_now(localized=False)
        sleep(3)
        localtime = timezone_aware_now(localized=True)

        assert utctime.tzinfo is not None
        assert localtime.tzinfo is not None
        assert utctime.tzinfo != localtime.tzinfo
        assert utctime != localtime
        # will not have been created at the same time
        assert utctime.astimezone().tzinfo == localtime.tzinfo


class TestProfiling:
    def test_profiling(self) -> None:
        with prepare_profiler(start=False) as profiler:
            profiler.runcall(lambda: 1 + 1)

            assert len(profiler.getstats()) == 1 + 1  # type: ignore

        with prepare_profiler(start=True) as profiler:
            profiler.runcall(lambda: 1 + 1)

            assert len(profiler.getstats()) > 1 + 1  # type: ignore


class TestMessagepack:
    def test_messagepack(self) -> None:
        payload = {"hello": "world", "foo": "bar"}

        packed = pack_messagepack(payload)
        unpacked = cast(dict[str, str], unpack_messagepack(packed))

        assert unpacked == payload


class TestLogging:
    def test_rich_logging(self) -> None:
        assert configure_rich_logger("INFO").level == logging.INFO
        assert configure_rich_logger("DEBUG").level == logging.DEBUG
        assert configure_rich_logger("WARNING").level == logging.WARNING
        assert configure_rich_logger("ERROR").level == logging.ERROR
        assert configure_rich_logger("CRITICAL").level == logging.CRITICAL
        assert configure_rich_logger(logging.INFO).level == logging.INFO
        assert configure_rich_logger(logging.DEBUG).level == logging.DEBUG
        assert configure_rich_logger(logging.WARNING).level == logging.WARNING
        assert configure_rich_logger(logging.ERROR).level == logging.ERROR
        assert configure_rich_logger(logging.CRITICAL).level == logging.CRITICAL

    @pytest.mark.asyncio
    async def test_dislog_integration(self) -> None:
        await make_async(configure_rich_logger)("INFO")  # type: ignore
        base64url = (
            b"aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE0Njk1NzgwNzQ2MDAyNDMzMC9BVUQyd3hhN01nMEMxeU1kME5u"
            b"VHNvQ083dmFBNHZ6ZGwyTzJUWUpYX2RXazNMY1A2MndiUEJTTnQxRnhtNy0zUG9wWg=="
        )
        url = base64.b64decode(base64url).decode("utf-8")
        handler = await add_remote_logger(url)
        handler.close()
        await asyncio.sleep(3)  # let it run


class TestAsyncio:
    @pytest.mark.asyncio
    async def test_make_async(self) -> None:
        aprint = make_async(print)

        assert await aprint("hello") is None  # type: ignore
        assert aprint is make_async(print)  # should be cached

    def test_make_sync(self) -> None:
        # This also tests run_coroutine_managed
        async def async_test() -> Literal[True]:
            return True

        sync_test = make_sync(async_test)
        assert sync_test() is True
        assert sync_test is make_sync(async_test)  # should be cached
