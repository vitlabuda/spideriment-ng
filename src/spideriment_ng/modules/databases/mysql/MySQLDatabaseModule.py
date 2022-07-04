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
from typing import Final, Optional, Sequence, Tuple, Any, Callable
import enum
import functools
import warnings
import os.path
import glob
import contextlib
import aiomysql
from datalidator.blueprints.impl.ObjectBlueprint import ObjectBlueprint
from spideriment_ng.SpiderimentConstants import SpiderimentConstants
from spideriment_ng.helpers.FlagCarrier import FlagCarrier
from spideriment_ng.helpers.CrawlingErrorReason import CrawlingErrorReason
from spideriment_ng.helpers.containers.document.DocumentContainer import DocumentContainer
from spideriment_ng.helpers.containers.document.URLContainer import URLContainer
from spideriment_ng.modules.ModuleInfo import ModuleInfo
from spideriment_ng.modules.ModuleType import ModuleType
from spideriment_ng.modules.databases.CrawledURLHandleIface import CrawledURLHandleIface
from spideriment_ng.modules.databases.DatabaseModuleIface import DatabaseModuleIface
from spideriment_ng.modules.databases.mysql._MySQLDatabaseModuleConfigModel import _MySQLDatabaseModuleConfigModel
from spideriment_ng.modules.databases.mysql._MySQLCrawledURLHandle import _MySQLCrawledURLHandle
from spideriment_ng.modules.databases.mysql._constants.Database import Database  # noqa
from spideriment_ng.modules.databases.mysql._constants.EnumValues import EnumValues  # noqa
from spideriment_ng.modules.databases.mysql._constants.Functions import Functions  # noqa
from spideriment_ng.modules.databases.mysql._constants.Procedures import Procedures  # noqa
from spideriment_ng.modules.databases.mysql._constants.SelectQueries import SelectQueries  # noqa
from spideriment_ng.modules.databases.mysql.exc.MySQLDatabaseModuleBaseExc import MySQLDatabaseModuleBaseExc
from spideriment_ng.modules.databases.mysql.exc.MySQLConnectionFailureExc import MySQLConnectionFailureExc
from spideriment_ng.modules.databases.mysql.exc.MySQLDisconnectionFailureExc import MySQLDisconnectionFailureExc
from spideriment_ng.modules.databases.mysql.exc.MySQLCommunicationFailureExc import MySQLCommunicationFailureExc
from spideriment_ng.modules.databases.mysql.exc.MySQLResultFetchFailureExc import MySQLResultFetchFailureExc
from spideriment_ng.modules.databases.mysql.exc.MySQLNoMoreLinksToCrawlExc import MySQLNoMoreLinksToCrawlExc
from spideriment_ng.modules.databases.mysql.exc.MySQLUnacceptableRedirectedURLExc import MySQLUnacceptableRedirectedURLExc
from spideriment_ng.modules.databases.mysql.exc.MySQLLockingFailureExc import MySQLLockingFailureExc


class MySQLDatabaseModule(DatabaseModuleIface):
    class _ModuleState(enum.Enum):
        UNPREPARED = 10
        OPERATIONAL = 20
        CLEANED_UP = 30
        BROKEN = 40

    _MODULE_INFO: Final[ModuleInfo] = ModuleInfo(
        type_=ModuleType.DATABASE,
        name="mysql",
        configuration_blueprint=ObjectBlueprint(_MySQLDatabaseModuleConfigModel)
    )

    # NOTE: This module does not support recrawling of documents (a URL may be crawled only once) and ensures that only
    #  one worker task globally (!) can crawl a specific URL at the same time. However, this behaviour is not required
    #  and/or enforced by the rest of this program in any way - a fully working database module which does not behave
    #  in the aforementioned ways could be implemented.

    @classmethod
    def get_module_info(cls) -> ModuleInfo:
        return cls._MODULE_INFO

    @staticmethod  # Decorator
    def _mysql_exception_handling_context(func: Callable) -> Callable:
        @functools.wraps(func)
        def _exception_handling_wrapper_function(self, *args, **kwargs) -> Any:
            try:
                return func(self, *args, **kwargs)
            except (MySQLDatabaseModuleBaseExc, AssertionError) as e:
                raise e
            except Exception as f:  # It is not clear what exceptions does 'aiomysql' raise
                raise MySQLCommunicationFailureExc(self._mysql_host, self._mysql_port, str(f))

        return _exception_handling_wrapper_function

    def __init__(self, mysql_client: aiomysql.Pool, mysql_host: str, mysql_port: int, instance_name: str):
        self._mysql_client: Final[aiomysql.Pool] = mysql_client
        self._mysql_host: Final[str] = mysql_host
        self._mysql_port: Final[int] = mysql_port
        self._instance_name: Final[str] = instance_name
        self._state: MySQLDatabaseModule._ModuleState = self.__class__._ModuleState.UNPREPARED
        self._active_crawler_id: Optional[int] = None

    @classmethod
    async def create_instance(cls, module_options: _MySQLDatabaseModuleConfigModel, instance_name: str) -> MySQLDatabaseModule:
        warnings.filterwarnings("ignore", module="aiomysql")  # Database warnings should be silenced

        mysql_host = module_options.mysql_host
        mysql_port = module_options.mysql_port
        connection_pool_size = module_options.connection_pool_size

        try:
            mysql_client = await aiomysql.create_pool(minsize=connection_pool_size, maxsize=connection_pool_size,
                                                      host=mysql_host, port=mysql_port,
                                                      user=module_options.mysql_user, password=module_options.mysql_password,
                                                      db=module_options.mysql_db, charset=Database.CHARACTER_SET, autocommit=False)
        except AssertionError as e:
            raise e
        except Exception as f:  # It is not clear what exceptions does 'aiomysql' raise
            raise MySQLConnectionFailureExc(mysql_host, mysql_port, str(f))

        module_instance = cls(mysql_client, mysql_host, mysql_port, instance_name)
        await module_instance._prepare_database_on_client_connection()

        return module_instance

    async def destroy_instance(self) -> None:
        assert (self._state == self.__class__._ModuleState.OPERATIONAL)

        pending_exception = None

        try:
            await self._cleanup_database_on_client_disconnection()
        finally:
            try:
                self._mysql_client.close()
                await self._mysql_client.wait_closed()
            except Exception as e:
                pending_exception = e

        # This "prioritizes" exceptions raised in the 'try' block over exceptions raised in the 'finally' block
        #  (Exceptions from the 'finally' block are re-raised only if no exceptions were raised in the 'try' block)
        if isinstance(pending_exception, AssertionError):
            raise pending_exception
        if pending_exception is not None:
            raise MySQLDisconnectionFailureExc(self._mysql_host, self._mysql_port, str(pending_exception))

    @_mysql_exception_handling_context
    async def _prepare_database_on_client_connection(self) -> None:
        assert (self._state == self.__class__._ModuleState.UNPREPARED)

        try:
            await self._create_database_objects()
            await self._register_active_crawler()
        except Exception as e:
            self._state = self.__class__._ModuleState.BROKEN
            raise e
        else:
            self._state = self.__class__._ModuleState.OPERATIONAL

    async def _create_database_objects(self) -> None:
        db_object_files_glob = os.path.join(os.path.dirname(os.path.realpath(__file__)), "db_objects/*.sql")

        create_queries = []
        for filepath in sorted(glob.glob(db_object_files_glob)):
            with open(filepath) as file:
                create_queries.append(file.read())

        assert (len(create_queries) > 0)

        async with self._unsafe_mysql_cursor() as cursor:
            # 'CREATE ...' queries cause an implicit commit (see https://dev.mysql.com/doc/refman/8.0/en/implicit-commit.html)
            for create_query in create_queries:
                await cursor.execute(query=create_query, args=None)

    async def _register_active_crawler(self) -> None:
        assert (self._active_crawler_id is None)

        async with self._safe_mysql_cursor() as (cursor, success_flag_carrier):
            self._active_crawler_id = await self._call_mysql_function(
                cursor=cursor,
                function_name=Functions.REGISTER_ACTIVE_CRAWLER,
                args=(self._instance_name, "Spideriment-NG", SpiderimentConstants.PROGRAM_VERSION),
                result_filter=int
            )
            success_flag_carrier.set(True)  # If all the previous code succeeds... (i.e. it does not raise an exception)

    @_mysql_exception_handling_context
    async def _cleanup_database_on_client_disconnection(self) -> None:
        assert (self._state == self.__class__._ModuleState.OPERATIONAL)

        try:
            await self._unregister_active_crawler()
        except Exception as e:
            self._state = self.__class__._ModuleState.BROKEN
            raise e
        else:
            self._state = self.__class__._ModuleState.CLEANED_UP

    async def _unregister_active_crawler(self) -> None:
        assert (self._active_crawler_id is not None)

        async with self._safe_mysql_cursor() as (cursor, success_flag_carrier):
            await self._call_mysql_procedure(
                cursor=cursor,
                procedure_name=Procedures.UNREGISTER_ACTIVE_CRAWLER,
                args=(self._active_crawler_id,)
            )
            success_flag_carrier.set(True)  # If all the previous code succeeds... (i.e. it does not raise an exception)

        self._active_crawler_id = None

    @_mysql_exception_handling_context
    async def announce_start_urls(self, validated_absolute_start_urls: Sequence[URLContainer]) -> None:
        assert (self._state == self.__class__._ModuleState.OPERATIONAL)
        assert (len(validated_absolute_start_urls) > 0)
        for url in validated_absolute_start_urls:
            assert (url.is_validated() and url.is_certainly_absolute())

        async with self._safe_mysql_cursor() as (cursor, success_flag_carrier):
            for start_url_container in validated_absolute_start_urls:
                await self._call_mysql_procedure(
                    cursor=cursor,
                    procedure_name=Procedures.STORE_START_URL_TO_LINKS,
                    args=(start_url_container.get_url(),)
                )
            success_flag_carrier.set(True)  # If all the previous code succeeds... (i.e. it does not raise an exception)

    @_mysql_exception_handling_context
    async def get_url_to_crawl(self) -> CrawledURLHandleIface:
        assert (self._state == self.__class__._ModuleState.OPERATIONAL)
        assert (self._active_crawler_id is not None)

        async with self._safe_mysql_cursor() as (cursor, success_flag_carrier):
            delayed = True
            link_id = await self._call_mysql_function(
                cursor=cursor,
                function_name=Functions.GET_LINK_TO_CRAWL_FROM_DELAYED_LINKS,
                args=(self._active_crawler_id,),
                result_filter=self._none_or_int_result_filter
            )
            if link_id is None:
                delayed = False
                link_id = await self._call_mysql_function(
                    cursor=cursor,
                    function_name=Functions.GET_LINK_TO_CRAWL_FROM_LINKS,
                    args=(self._active_crawler_id,),
                    result_filter=self._none_or_int_result_filter
                )
                if link_id is None:
                    raise MySQLNoMoreLinksToCrawlExc()

            link_url = await self._run_select_query_and_fetch_result(
                cursor=cursor,
                query=SelectQueries.GET_URL_BY_LINK_ID,
                args=(link_id,),
                result_filter=str
            )

            success_flag_carrier.set(True)  # If all the previous code succeeds... (i.e. it does not raise an exception)

        return _MySQLCrawledURLHandle(
            link_id=link_id,
            url_in_container=URLContainer(validated=False, certainly_absolute=True, url=link_url),
            delayed=delayed,
            redirected=False
        )

    @_mysql_exception_handling_context
    async def announce_redirected_url(self, original_url: CrawledURLHandleIface, validated_absolute_redirected_url: URLContainer) -> CrawledURLHandleIface:
        assert (self._state == self.__class__._ModuleState.OPERATIONAL)
        assert (self._active_crawler_id is not None)
        assert (isinstance(original_url, _MySQLCrawledURLHandle) and (not original_url.is_redirected()))
        assert (validated_absolute_redirected_url.is_validated() and validated_absolute_redirected_url.is_certainly_absolute())

        redirected_url = validated_absolute_redirected_url.get_url()
        assert (original_url.get_url_in_container().get_url() != redirected_url)

        async with self._safe_mysql_cursor() as (cursor, success_flag_carrier):
            delayed = True
            link_id = await self._call_mysql_function(
                cursor=cursor,
                function_name=Functions.HANDLE_REDIRECTED_URL_IN_DELAYED_LINKS,
                args=(self._active_crawler_id, redirected_url),
                result_filter=self._none_or_int_result_filter
            )
            if link_id is None:
                delayed = False
                link_id = await self._call_mysql_function(
                    cursor=cursor,
                    function_name=Functions.HANDLE_REDIRECTED_URL_IN_LINKS,
                    args=(self._active_crawler_id, redirected_url),
                    result_filter=self._none_or_int_result_filter
                )
                if link_id is None:
                    raise MySQLUnacceptableRedirectedURLExc(redirected_url)

            # This function already has the URL, but just to be sure, it is re-fetched from the database (to prevent
            #  certain inconsistencies that cannot happen if the program operates as it should - however, mistakes can
            #  happen)
            link_url = await self._run_select_query_and_fetch_result(
                cursor=cursor,
                query=SelectQueries.GET_URL_BY_LINK_ID,
                args=(link_id,),
                result_filter=str
            )

            success_flag_carrier.set(True)  # If all the previous code succeeds... (i.e. it does not raise an exception)

        return _MySQLCrawledURLHandle(
            link_id=link_id,
            url_in_container=URLContainer(validated=False, certainly_absolute=True, url=link_url),
            delayed=delayed,
            redirected=True
        )

    @_mysql_exception_handling_context
    async def finish_crawling_with_delay(self, original_url: CrawledURLHandleIface, delay_seconds: int) -> None:
        assert (self._state == self.__class__._ModuleState.OPERATIONAL)
        assert (isinstance(original_url, _MySQLCrawledURLHandle) and (not original_url.is_redirected()))
        assert (delay_seconds > 0)

        async with self._safe_mysql_cursor() as (cursor, success_flag_carrier):
            await self._call_mysql_procedure(
                cursor=cursor,
                procedure_name=Procedures.FINISH_CRAWLING_WITH_DELAY,
                args=(original_url.get_link_id(), delay_seconds)
            )
            success_flag_carrier.set(True)  # If all the previous code succeeds... (i.e. it does not raise an exception)

    @_mysql_exception_handling_context
    async def finish_crawling_with_error(self, original_url: CrawledURLHandleIface, redirected_url: Optional[CrawledURLHandleIface], error_reason: CrawlingErrorReason) -> None:
        assert (self._state == self.__class__._ModuleState.OPERATIONAL)
        assert (isinstance(original_url, _MySQLCrawledURLHandle) and (not original_url.is_redirected()))
        if redirected_url is not None:
            assert (isinstance(redirected_url, _MySQLCrawledURLHandle) and redirected_url.is_redirected())
            assert (original_url.get_link_id() != redirected_url.get_link_id())

        erroneous_link_ids = [original_url.get_link_id()]
        if redirected_url is not None:
            erroneous_link_ids.append(redirected_url.get_link_id())
        error_reason_mysql_enum_value = EnumValues.get_link_crawling_error_reason(error_reason),

        async with self._safe_mysql_cursor() as (cursor, success_flag_carrier):
            for erroneous_link_id in erroneous_link_ids:
                await self._call_mysql_procedure(
                    cursor=cursor,
                    procedure_name=Procedures.FINISH_CRAWLING_WITH_ERROR,
                    args=(erroneous_link_id, error_reason_mysql_enum_value)
                )
            success_flag_carrier.set(True)  # If all the previous code succeeds... (i.e. it does not raise an exception)

    @_mysql_exception_handling_context
    async def finish_crawling_with_success(self, original_url: CrawledURLHandleIface, redirected_url: Optional[CrawledURLHandleIface], validated_document: DocumentContainer) -> None:
        assert (self._state == self.__class__._ModuleState.OPERATIONAL)
        assert (isinstance(original_url, _MySQLCrawledURLHandle) and (not original_url.is_redirected()))
        if redirected_url is not None:
            assert (isinstance(redirected_url, _MySQLCrawledURLHandle) and redirected_url.is_redirected())
            assert (original_url.get_link_id() != redirected_url.get_link_id())
        assert validated_document.is_validated()
        for content_snippet in validated_document.get_content_snippets():
            assert content_snippet.is_validated()
        for link in validated_document.get_links():
            assert link.is_validated()
            assert link.get_href_url().is_validated()
        for image in validated_document.get_images():
            assert image.is_validated()
            assert image.get_src_url().is_validated()

        original_link_id = original_url.get_link_id()
        final_link_id = (redirected_url.get_link_id() if (redirected_url is not None) else original_link_id)

        async with self._safe_mysql_cursor() as (cursor, success_flag_carrier):
            document_id = await self._call_mysql_function(
                cursor=cursor,
                function_name=Functions.FINISH_CRAWLING_WITH_SUCCESS,
                args=(original_link_id, final_link_id, validated_document.get_file_type(), validated_document.get_language(), validated_document.get_author(), validated_document.get_title(), validated_document.get_description()),
                result_filter=int
            )
            for keyword in validated_document.get_keywords():
                await self._call_mysql_procedure(
                    cursor=cursor,
                    procedure_name=Procedures.ADD_KEYWORD_TO_DOCUMENT,
                    args=(document_id, keyword)
                )
            for content_snippet in validated_document.get_content_snippets():
                snippet_type_mysql_enum_value = EnumValues.get_content_snippet_type(content_snippet.get_snippet_type()),
                await self._call_mysql_procedure(
                    cursor=cursor,
                    procedure_name=Procedures.ADD_CONTENT_SNIPPET_TO_DOCUMENT,
                    args=(document_id, snippet_type_mysql_enum_value, content_snippet.get_snippet_text())
                )
            for link in validated_document.get_links():
                await self._call_mysql_procedure(
                    cursor=cursor,
                    procedure_name=Procedures.ADD_LINK_TO_DOCUMENT,
                    args=(document_id, link.get_href_url().get_url(), link.get_link_text())
                )
            for image in validated_document.get_images():
                await self._call_mysql_procedure(
                    cursor=cursor,
                    procedure_name=Procedures.ADD_IMAGE_TO_DOCUMENT,
                    args=(document_id, image.get_src_url().get_url(), image.get_alt_text(), image.get_title_text())
                )
            success_flag_carrier.set(True)  # If all the previous code succeeds... (i.e. it does not raise an exception)

    async def _call_mysql_procedure(self, cursor: aiomysql.Cursor, procedure_name: str, args: Tuple[Any, ...]) -> None:
        assert (len(procedure_name) > 0)

        await cursor.execute(
            query=f"CALL `{procedure_name}`({self._generate_query_args_placeholders(len(args))});",
            args=args
        )

    async def _call_mysql_function(self, cursor: aiomysql.Cursor, function_name: str, args: Tuple[Any, ...], result_filter: Callable[[Any], Any]) -> Any:
        assert (len(function_name) > 0)

        return await self._run_select_query_and_fetch_result(
            cursor=cursor,
            query=f"SELECT `{function_name}`({self._generate_query_args_placeholders(len(args))}) AS `fn_return_value`;",
            args=args,
            result_filter=result_filter
        )

    def _generate_query_args_placeholders(self, count: int) -> str:
        assert (count >= 0)

        return ", ".join(["%s"] * count)

    async def _run_select_query_and_fetch_result(self, cursor: aiomysql.Cursor, query: str, args: Optional[Tuple[Any, ...]], result_filter: Callable[[Any], Any]) -> Any:
        query = query.strip()
        assert query.upper().startswith("SELECT ")

        await cursor.execute(query=query, args=args)
        fetched_values = await cursor.fetchall()

        if len(fetched_values) != 1 or len(fetched_values[0]) != 1:
            raise MySQLResultFetchFailureExc(query)

        try:
            return result_filter(fetched_values[0][0])
        except Exception:
            raise MySQLResultFetchFailureExc(query)

    def _none_or_int_result_filter(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        return int(value)

    @contextlib.asynccontextmanager
    async def _unsafe_mysql_cursor(self) -> aiomysql.Cursor:
        async with self._mysql_client.acquire() as connection:
            async with connection.cursor() as cursor:
                yield cursor

    @contextlib.asynccontextmanager
    async def _safe_mysql_cursor(self) -> Tuple[aiomysql.Cursor, FlagCarrier]:
        async with self._mysql_client.acquire() as connection:
            async with connection.cursor() as cursor:
                success_flag_carrier = FlagCarrier(initial_value=False)
                pending_exception = None

                try:
                    await cursor.execute("SET autocommit = 0;")
                    await self._acquire_mysql_lock(cursor)
                    await cursor.execute("START TRANSACTION;")

                    yield cursor, success_flag_carrier
                finally:
                    try:
                        await cursor.execute("COMMIT;" if success_flag_carrier.get() else "ROLLBACK;")
                    except Exception as e:
                        pending_exception = e

                    try:
                        await self._release_mysql_lock(cursor)
                    except Exception as e:
                        pending_exception = e

                # This "prioritizes" exceptions raised in the 'try' block over exceptions raised in the 'finally' block
                #  (Exceptions from the 'finally' block are re-raised only if no exceptions were raised in the 'try' block)
                if pending_exception is not None:
                    raise pending_exception

    async def _acquire_mysql_lock(self, cursor: aiomysql.Cursor) -> None:
        # This lock, among other things, ensures that more workers cannot get the same URL for crawling, which is
        #  absolutely essential for this program!

        # https://dev.mysql.com/doc/refman/8.0/en/locking-functions.html#function_get-lock
        get_lock_return_value = await self._call_mysql_function(
            cursor=cursor,
            function_name="GET_LOCK",
            args=(Database.LOCK_NAME, 2147483647),  # MariaDB does not accept negative (= infinite) timeouts!
            result_filter=self._none_or_int_result_filter
        )

        if get_lock_return_value != 1:
            raise MySQLLockingFailureExc(get_lock_return_value)

    async def _release_mysql_lock(self, cursor: aiomysql.Cursor) -> None:
        # https://dev.mysql.com/doc/refman/8.0/en/locking-functions.html#function_release-lock
        await self._call_mysql_function(
            cursor=cursor,
            function_name="RELEASE_LOCK",
            args=(Database.LOCK_NAME,),
            result_filter=self._none_or_int_result_filter
        )
