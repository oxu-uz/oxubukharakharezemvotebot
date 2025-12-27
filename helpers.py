import re

import pandas as pd
import psycopg2
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT, CHANNEL_ID, CHANNEL_URL, CHANNEL_URL2


async def exel_import_areas():
        DB_CONFIG = {
            "dbname": DB_NAME,
            "user": DB_USER,
            "password": DB_PASS,
            "host": DB_HOST,
            "port": DB_PORT
        }

        df = pd.read_excel("uploads/areas.xlsx")

        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for _, row in df.iterrows():
            cursor.execute(
                """
                INSERT INTO areas (name, total_votes)
                VALUES (%s, %s)
                ON CONFLICT (name) DO NOTHING;
                """,
                (row["Guruhlar"], "0")
            )

        conn.commit()
        cursor.close()
        conn.close()

        print("🔥 Areas have been created !")
        return "🔥 Areas have been created !"


async def is_user_subscribed(user_id: int, bot) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

async def join_channels_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)

    buttons = [
        InlineKeyboardButton(
            text="📢 1-kanalga obuna",
            url=CHANNEL_URL
        ),
        InlineKeyboardButton(
            text="📢 2-kanalga obuna",
            url=CHANNEL_URL2
        ),
        InlineKeyboardButton(
            text="✅ Tekshirish",
            callback_data="check_subscribe"
        )
    ]

    markup.add(*buttons)
    return markup



def subscribe_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📢 1-kanalga obuna bo‘lish", url="https://t.me/kanal_birinchi"),
        InlineKeyboardButton("📢 2-kanalga obuna bo‘lish", url="https://t.me/kanal_ikkinchi"),
        InlineKeyboardButton("🔄 Tekshirish", callback_data="check_sub")
    )
    return kb


def remove_all_whitespace(text: str) -> str:
    return re.sub(r"\s+", "", text)
