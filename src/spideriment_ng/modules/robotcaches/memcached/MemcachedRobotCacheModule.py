#!/bin/false

# Copyright (c) 2022 Vít Labuda. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#  1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#     disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#     following disclaimer in the documentation and/or other materials provided with the distribution.
#  3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#     products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from __future__ import annotations
from typing import Final
import hashlib
import urllib.robotparser
import aiomcache
from datalidator.blueprints.impl.ObjectBlueprint import ObjectBlueprint
from spideriment_ng.modules.ModuleInfo import ModuleInfo
from spideriment_ng.modules.ModuleType import ModuleType
from spideriment_ng.modules.robotcaches.RobotCacheModuleIface import RobotCacheModuleIface
from spideriment_ng.modules.robotcaches.memcached._MemcachedRobotCacheModuleConfigModel import _MemcachedRobotCacheModuleConfigModel
from spideriment_ng.modules.robotcaches.memcached.exc.MemcachedConnectionFailureExc import MemcachedConnectionFailureExc
from spideriment_ng.modules.robotcaches.memcached.exc.MemcachedDisconnectionFailureExc import MemcachedDisconnectionFailureExc
from spideriment_ng.modules.robotcaches.memcached.exc.MemcachedCommunicationFailureExc import MemcachedCommunicationFailureExc
from spideriment_ng.modules.robotcaches.memcached.exc.MemcachedCacheMissExc import MemcachedCacheMissExc


class MemcachedRobotCacheModule(RobotCacheModuleIface):
    _MODULE_INFO: Final[ModuleInfo] = ModuleInfo(
        type_=ModuleType.ROBOT_CACHE,
        name="memcached",
        configuration_blueprint=ObjectBlueprint(_MemcachedRobotCacheModuleConfigModel)
    )

    _MEMCACHED_KEY_PATTERN: Final[str] = "spideriment_ng.memcached_robot_cache_module.{supplied_key_hash}"
    _ENCODING: Final[str] = "utf-8"

    @classmethod
    def get_module_info(cls) -> ModuleInfo:
        return cls._MODULE_INFO

    def __init__(self, memcached_client: aiomcache.Client, memcached_host: str, memcached_port: int):
        self._memcached_client: Final[aiomcache.Client] = memcached_client
        self._memcached_host: Final[str] = memcached_host
        self._memcached_port: Final[int] = memcached_port
        self._operational: bool = True

    @classmethod
    async def create_instance(cls, module_options: _MemcachedRobotCacheModuleConfigModel, instance_name: str) -> MemcachedRobotCacheModule:
        memcached_host = module_options.memcached_host
        memcached_port = module_options.memcached_port
        connection_pool_size = module_options.connection_pool_size

        try:
            memcached_client = aiomcache.Client(host=memcached_host, port=memcached_port, pool_size=connection_pool_size, pool_minsize=connection_pool_size)
            await memcached_client.version()  # Connects to the server -> initializes the connection pool
        except AssertionError as e:
            raise e
        except Exception as f:
            raise MemcachedConnectionFailureExc(memcached_host, memcached_port, str(f))

        return cls(memcached_client, memcached_host, memcached_port)

    async def destroy_instance(self) -> None:
        assert self._operational
        self._operational = False

        try:
            await self._memcached_client.close()
        except AssertionError as e:
            raise e
        except Exception as f:
            raise MemcachedDisconnectionFailureExc(self._memcached_host, self._memcached_port, str(f))

    async def retrieve_from_cache(self, key: str) -> urllib.robotparser.RobotFileParser:
        assert self._operational

        memcached_key = self._make_memcached_key_from_supplied_key(key)

        try:
            retrieved_value = await self._memcached_client.get(key=memcached_key, default=None)  # noqa
        except AssertionError as e:
            raise e
        except OSError as f:
            raise MemcachedCommunicationFailureExc(self._memcached_host, self._memcached_port, str(f))
        except Exception:  # noqa; If the server/client fails to get the value, it is considered a cache miss
            retrieved_value = None

        if retrieved_value is None:
            raise MemcachedCacheMissExc(key)

        return self._bytes_to_robot_parser(retrieved_value)

    async def put_into_cache(self, key: str, robot_parser: urllib.robotparser.RobotFileParser) -> None:
        assert self._operational

        memcached_key = self._make_memcached_key_from_supplied_key(key)
        memcached_value = self._robot_parser_to_bytes(robot_parser)

        try:
            await self._memcached_client.set(key=memcached_key, value=memcached_value)
        except AssertionError as e:
            raise e
        except OSError as f:
            raise MemcachedCommunicationFailureExc(self._memcached_host, self._memcached_port, str(f))
        except Exception:  # noqa; If the server/client fails to set the value, it is ignored, since it can be caused, for example, by too big of a value
            pass

    def _make_memcached_key_from_supplied_key(self, supplied_key: str) -> bytes:
        supplied_key_hash = hashlib.sha384(supplied_key.encode(self.__class__._ENCODING)).hexdigest()
        memcached_key_str = self.__class__._MEMCACHED_KEY_PATTERN.format(supplied_key_hash=supplied_key_hash)

        return memcached_key_str.encode(self.__class__._ENCODING)

    def _bytes_to_robot_parser(self, bytes_: bytes) -> urllib.robotparser.RobotFileParser:
        lines = bytes_.decode(self.__class__._ENCODING).splitlines()

        robot_parser = urllib.robotparser.RobotFileParser()
        robot_parser.parse(lines)

        return robot_parser

    def _robot_parser_to_bytes(self, robot_parser: urllib.robotparser.RobotFileParser) -> bytes:
        return str(robot_parser).encode(self.__class__._ENCODING)
