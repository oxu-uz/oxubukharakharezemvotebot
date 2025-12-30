import hashlib
import random
import uuid
from gc import callbacks

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import *

from data.config import CHANNEL_SUBSCRIBE_ID_1, CHANNEL_SUBSCRIBE_ID_2, BOT_USERNAME
from helpers import is_user_subscribed, join_channels_keyboard, remove_all_whitespace
from loader import dp, bot, db
from message.function.get_keyboard_inline import make_inline_button
from states.states import StudentState
from voises.voice_path import voices_path


@dp.message_handler(text=['❌ Bekor qilish'], state='*')
async def cancel(message: Message, state: FSMContext):
    await state.finish()
    return


@dp.message_handler(commands=["help"], chat_type='private', state='*')
async def bot_start(message: Message, state: FSMContext):
    await state.finish()
    await message.answer(f"Yordam uchun @beeliberty ga murojaat qiling!")


@dp.message_handler(CommandStart(), chat_type='private', state='*')
async def bot_start(message: Message, state: FSMContext):
    await state.finish()
    win_groups = await db.get_win_areas()
    print('win_groups', win_groups)
    top_groups = InlineKeyboardMarkup(row_width=2)
    for group in win_groups:
        button = InlineKeyboardButton(text=f"{group['area_name']} - {group['total']} ta ovoz",
                                      url=f"https://t.me/{BOT_USERNAME}?start={group['area_name']}")
        top_groups.add(button)
    top_groups.add(
        InlineKeyboardButton(
            text="🔍 Guruh tanlash",
            switch_inline_query_current_chat=""
        )
    )
    await message.answer("Eng ko'p ovoz yig'gan guruhlar :", reply_markup=top_groups)

    args = message.get_args()
    check = await db.check_user(message.chat.id)
    if not check:
        if args:
            for channel in [CHANNEL_SUBSCRIBE_ID_1, CHANNEL_SUBSCRIBE_ID_2]:
                member = await bot.get_chat_member(
                    chat_id=channel,
                    user_id=message.from_user.id
                )

                if member.status not in ("member", "administrator", "creator"):
                    await message.answer(
                        "❌ Avval barcha kanallarga obuna bo‘ling.", reply_markup=await join_channels_keyboard()
                    )
                    return
                if member.status in ("member", "administrator", "creator"):
                    area = await db.get_area(args)
                    print('area===', area)
                    print(area[0]['id'])
                    count_users = await db.count_users(area[0]['id'])
                    # print(count_users)
                    await state.update_data(
                        id=area[0][0],
                        name=area[0][1],
                        total_votes=count_users,
                    )
                    await message.answer(
                        f"{args} guruhiga ovoz beryapsiz\nGuruhning hozirgi ko'rsatkichi: {area[0][2]}",
                        reply_markup=await make_inline_button(text=area[0][1], callback_data=f"area_id_{area[0][0]}"))
                    await StudentState.get_vote.set()
                    return

        # if not await is_user_subscribed(message.from_user.id, message.bot):
        #     await message.answer("🚫 Avval kanalga obuna bo‘ling", reply_markup=await join_channels_keyboard())
        #     return
        for channel in [CHANNEL_SUBSCRIBE_ID_1, CHANNEL_SUBSCRIBE_ID_2]:
            member = await bot.get_chat_member(
                chat_id=channel,
                user_id=message.from_user.id
            )

            if member.status not in ("member", "administrator", "creator"):
                await message.answer(
                    "❌ Avval barcha kanallarga obuna bo‘ling.", reply_markup=await join_channels_keyboard()
                )
                return

        await StudentState.group.set()
    else:
        await message.answer("Siz allaqachon ovoz bergansiz!\nFaqat 1 marta ovoz berish mumkin.")


from aiogram import types


@dp.callback_query_handler(text="check_subscribe", state='*')
async def check_subscription(call: types.CallbackQuery):
    user_id = call.from_user.id
    for channel in [CHANNEL_SUBSCRIBE_ID_1, CHANNEL_SUBSCRIBE_ID_2]:
        member = await call.bot.get_chat_member(
            chat_id=channel,
            user_id=user_id
        )

        if member.status not in ("member", "administrator", "creator"):
            await call.message.answer(
                "❌ Avval barcha kanallarga obuna bo‘ling.", reply_markup=await join_channels_keyboard()
            )
            await call.answer()
            return
    await call.answer()
    win_groups = await db.get_win_areas()

    top_groups = InlineKeyboardMarkup(row_width=2)
    for group in win_groups:
        button = InlineKeyboardButton(text=f"{group['total_votes']}|{group['name']}",
                                      url=f"https://t.me/{BOT_USERNAME}?start={group['name']}")
        top_groups.add(button)
    top_groups.add(
        InlineKeyboardButton(
            text="🔍 Guruh tanlash",
            switch_inline_query_current_chat=""
        )
    )
    await call.message.answer("Eng ko'p ovoz yig'gan guruhlar 10 ligi:", reply_markup=top_groups)
    await StudentState.group.set()


@dp.inline_handler(state='*')
async def inline_area_search(inline_query: types.InlineQuery):
    query_text = inline_query.query.strip()
    if len(query_text) < 3:
        await inline_query.answer([], cache_time=0)
        return
    plain_text = remove_all_whitespace(query_text)
    results = await db.search_areas(plain_text)
    articles = []

    for area_id, name in results:
        articles.append(
            types.InlineQueryResultArticle(
                id=str(area_id),
                title=name,
                input_message_content=types.InputTextMessageContent(
                    message_text=name
                )
            )
        )

    await inline_query.answer(articles, cache_time=0, is_personal=True)
    await StudentState.vote.set()


@dp.message_handler(chat_type='private', state=StudentState.vote)
async def voice(message: Message, state: FSMContext):
    check = await db.check_user(message.chat.id)
    if not check:
        area = await db.get_area(message.text)
        await state.update_data(
            id=area[0][0],
            name=area[0][1],
            total_votes=area[0][2],
        )
        await message.answer(
            f"{message.text} guruhiga ovoz beryapsiz\nGuruhning hozirgi ko'rsatkichi: {area[0][2]}",
            reply_markup=await make_inline_button(text=area[0][1], callback_data=f"area_id_{area[0][0]}"))
        await StudentState.get_vote.set()
    else:
        await message.answer('Siz allaqachon ovoz bergansiz! Faqat 1 marta ovoz berish mumkin.')

@dp.callback_query_handler(lambda c: c.data.startswith("area_id_"), state=StudentState.get_vote)
async def vote(call: CallbackQuery, state: FSMContext):
    for channel in [CHANNEL_SUBSCRIBE_ID_1, CHANNEL_SUBSCRIBE_ID_2]:
        member = await call.bot.get_chat_member(
            chat_id=channel,
            user_id=call.from_user.id
        )

        if member.status not in ("member", "administrator", "creator"):
            await call.message.answer(
                "❌ Avval barcha kanallarga obuna bo‘ling.", reply_markup=await join_channels_keyboard()
            )
            await call.answer()
            return
    random_int = random.randint(0, len(voices_path) - 1)
    random_voice = voices_path[random_int]
    await state.update_data(voice_code=random_voice['key'])
    await bot.send_audio(call.message.chat.id, InputFile(random_voice['value']), title='Quyidagi sonni kiriting:')
    await StudentState.recaptcha.set()


@dp.message_handler(state=StudentState.recaptcha)
async def recaptcha(message: Message, state: FSMContext):
    data = await state.get_data()
    if data['voice_code'] == message.text:
        total_vote = await db.count_users(data['id'])
        print(total_vote)
        update_vote = await db.update_votes(total_vote + 1, data['id'])
        print(update_vote)
        await db.create_user(
            telegram_id=message.from_user.id,
            name=message.from_user.full_name,
            username=message.from_user.username,
            area_id=data['id'],
        )
        await message.answer('Ovozingiz qabul qilindi!')
        await message.answer(f"{data['name']} guruh umumiy ovozlari soni: {int(data['total_votes']) + 1}")

        markup = InlineKeyboardMarkup()
        share_text = f"Men {data['name']} guruhiga ovoz berdim! Siz ham ovoz bering!"
        share_url = f"https://t.me/{BOT_USERNAME}?start={data['name']}"
        share_button = InlineKeyboardButton(text="Ulashish",
                                            url=f"https://t.me/share/url?text={share_text}&url={share_url}")
        markup.add(share_button)
        await message.answer(
            "Bu sizning referal havolangiz. Bu havolani yuborib o'z guruhingizga ovoz  yig'ishingiz mumkin!",
            reply_markup=markup)
    else:
        await message.answer('Xato son kiritildi. Qayta kiriting:')
        await StudentState.recaptcha.set()
