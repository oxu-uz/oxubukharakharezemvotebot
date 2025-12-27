from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create (self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
            port=config.DB_PORT
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def create_users_table(self):
        sql = """CREATE TABLE IF NOT EXISTS public.users (         
        id bigserial primary key,
        telegram_id bigint not null constraint users_telegram_id_unique unique,
        name       varchar(20),     
        username    varchar(255) null,
        area_id    integer null,
        created_at  timestamp(0) default now() not null,
        updated_at  timestamp(0) default now() not null
        );"""
        # sql_lang_index = """CREATE INDEX IF NOT EXISTS users_language_idx ON public.users USING btree (language);"""
        # sql_telegram_id_index = """CREATE INDEX IF NOT EXISTS users_telegram_id_idx ON public.users USING btree (telegram_id);"""
        await self.execute(sql, execute=True)
        # await self.execute(sql_lang_index, execute=True)
        # await self.execute(sql_telegram_id_index, execute=True)

    async def create_areas_table(self):
        sql = """CREATE TABLE IF NOT EXISTS public.areas (         
        id bigserial primary key,
        name varchar(50) not null unique,
        total_votes INTEGER default 0,
        created_at  timestamp(0) default now() not null,
        updated_at  timestamp(0) default now() not null
        );"""
        await self.execute(sql, execute=True)


    async def create_user(self, **kwargs):
        sql = """INSERT INTO public.users (telegram_id, name, username, area_id) VALUES ($1,$2,$3,$4)"""
        return await self.execute(sql, *kwargs.values(), execute=True)

    async def select_all_users(self):
        sql = "SELECT * FROM public.users"
        return await self.execute(sql, fetch=True)

    async def check_user(self, telegram_id):
        sql = "SELECT * FROM public.users WHERE telegram_id = $1"
        return await self.execute(sql, telegram_id, fetch=True)

    async def search_areas(self, search: str):
        sql = "SELECT id, name FROM areas WHERE name ILIKE $1"
        params = f"%{search}%"
        return await self.execute(sql, params, fetch=True)

    async def get_area(self, search: str):
        sql = "SELECT * FROM areas WHERE name ILIKE $1"
        params = f"%{search}%"
        return await self.execute(sql, params, fetch=True)

    async def get_win_areas(self):
        sql = "SELECT * FROM areas ORDER BY total_votes DESC LIMIT 10"
        return await self.execute(sql, fetch=True)

    async def update_votes(self,vote, area_id):
        sql = "UPDATE areas SET total_votes = $1 WHERE id = $2"
        return await self.execute(sql, vote, area_id, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM public.users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM public.users"
        return await self.execute(sql, fetchval=True)

    async def update_user_language(self, language, telegram_id):
        sql = "UPDATE public.users SET language=$1 WHERE telegram_id=$2"
        return await self.execute(sql, language, telegram_id, execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE public.users", execute=True)

    async def get_languages(self):
        sql = "SELECT * FROM public.languages"
        return await self.execute(sql, fetch=True)

    async def add_language(self, name, code, flag):
        sql = "INSERT INTO public.languages (name, code, flag) VALUES ($1,$2,$3)"
        return await self.execute(sql, name, code, flag, execute=True)

    async def get_word_types(self):
        sql = "SELECT * FROM public.types"
        return await self.execute(sql, fetch=True)

    async def add_word_type(self, name):
        sql = "INSERT INTO public.types (name) VALUES ($1)"
        return await self.execute(sql, name, execute=True)

    async def add_word(self, name, language_id):
        sql = "INSERT INTO public.words (name, language_id) VALUES ($1,$2) RETURNING id"
        return await self.execute(sql, name, language_id, fetchval=True)

    async def add_dictionary(self, word_id, translation_id):
        sql = "INSERT INTO public.dictionaries (word_id, translation_id) VALUES ($1,$2)"
        return await self.execute(sql, word_id, translation_id, execute=True)

    async def delete_word(self, word_id):
        sql = "DELETE FROM public.words WHERE id=$1"
        return await self.execute(sql, word_id, execute=True)

    async def get_random_test(self):
        sql = """select w.name as arabic_name, w2.name as uzbek_name, w.id as arabic_name_id, w2.id as uzbek_name_id from dictionaries
         left join words w on (w.id = dictionaries.translation_id) left join words w2 on (w2.id = dictionaries.word_id) 
         OFFSET floor(random() * (select count(*) from dictionaries)) LIMIT 100;"""
        return await self.execute(sql, fetch=True)

    async def get_random_options(self, word_id, limit, type_word):
        type_word = "translation_id" if type_word == "arabic" else "word_id"
        sql = f"""select w.name as name, w.id as id from dictionaries
                  left join words w on (w.id = dictionaries.{type_word}) 
                  where w.id != {word_id} OFFSET floor(random() * (select count(*) from dictionaries)) LIMIT {limit};"""
        return await self.execute(sql, fetch=True)
