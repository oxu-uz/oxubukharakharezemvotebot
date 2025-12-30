import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InputFile
from aiogram.utils.exceptions import BadWebhookAddrInfo

from data.config import ADMINS
from helpers import exel_import_areas
from loader import dp, bot, db
from states.admin import AdminState


@dp.message_handler(commands='admin', chat_type='private', state='*')
async def bot_start(message: Message, state: FSMContext):
    if str(message.from_user.id) in ADMINS:
        await state.finish()
        await message.answer(f"Assalomu aleykum admin {message.from_user.full_name}!")
        await message.answer(f"Guruhlar yuklash uchun:\n\n /areas\nbelgilangan gurugga ovoz berganlar:\n\n/group_report")
        await AdminState.area.set()


@dp.message_handler(commands='areas', chat_type='private', state=AdminState.area)
async def bot_start(message: Message):
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=InputFile('area_exel_example.png'),
                         caption=f"Exel fayl nomi areas.xlsx bo'lishi va ustunlar rasmdagiday nomlanishi kerak !")
    await AdminState.exel_area_seed.set()

@dp.message_handler(commands='group_report', chat_type='private', state=AdminState.area)
async def bot_start(message: Message):
    await message.answer("Guruh nomini aniq kiriting")
    await AdminState.area_users_send.set()

@dp.message_handler(chat_type='private', state=AdminState.area_users_send)
async def bot_start(message: Message):
    print(message.text)
    users = await db.get_area(message.text)
    print(users)
    count = await db.count_users(users[0])
    print(count)
    await message.answer(f"count: {count}\nid: {users['id']}\nname: {users['name']}\nusername: {users['username']}")
    await message.answer(f"Guruhlar yuklash uchun:\n\n /areas\nbelgilangan gurugga ovoz berganlar:\n\n/group_report")
    await AdminState.area.set()



@dp.message_handler(content_types=types.ContentType.DOCUMENT,  state=AdminState.exel_area_seed)
async def handle_excel(message: types.Message):
    document = message.document
    UPLOAD_DIR = "uploads"

    # Faqat Excel qabul qilamiz
    if not document.file_name.endswith(".xlsx"):
        await message.reply("❌ Faqat .xlsx Excel fayl yuboring.")
        await AdminState.exel_area_seed.set()

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_path = f"{UPLOAD_DIR}/{document.file_name}"

    file = await message.bot.get_file(document.file_id)
    await message.bot.download_file(file.file_path, file_path)

    area_create = await exel_import_areas()
    await message.answer(area_create)