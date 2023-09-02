"""MessagePack utilities for Fastapipostgres - Fastapipostgres.

Copyright (C) 2023  Parker Wahle

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""  # noqa: E501, B950
from __future__ import annotations

from typing import cast

import msgpack

from .asyncio import make_async


def pack_messagepack(payload: object) -> bytes:
    """Packs a payload into a MessagePack object."""
    return cast(bytes, msgpack.packb(payload, use_bin_type=True))


def unpack_messagepack(payload: bytes) -> object:
    """Unpacks a MessagePack object into a payload."""
    return msgpack.unpackb(payload, raw=False)


async_pack_messagepack = make_async(pack_messagepack)

async_unpack_messagepack = make_async(unpack_messagepack)

__all__ = ("pack_messagepack", "unpack_messagepack", "async_pack_messagepack", "async_unpack_messagepack")
