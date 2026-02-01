import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

from states import Creation
from data import HOMEWORLDS, BACKGROUNDS, ROLES

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=["start"])
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    kb = InlineKeyboardMarkup()
    for k, w in HOMEWORLDS.items():
        kb.add(InlineKeyboardButton(w["name"], callback_data=f"world:{k}"))
    await message.answer("Выберите родной мир:", reply_markup=kb)
    await Creation.choosing_world.set()


@dp.callback_query_handler(lambda c: c.data.startswith("world:"), state=Creation.choosing_world)
async def choose_world(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    await state.update_data(world=HOMEWORLDS[key])

    kb = InlineKeyboardMarkup()
    for k, bg in BACKGROUNDS.items():
        kb.add(InlineKeyboardButton(bg["name"], callback_data=f"bg:{k}"))

    await callback.message.answer("Выберите предысторию:", reply_markup=kb)
    await Creation.choosing_background.set()


@dp.callback_query_handler(lambda c: c.data.startswith("bg:"), state=Creation.choosing_background)
async def choose_bg(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    await state.update_data(background=BACKGROUNDS[key])

    kb = InlineKeyboardMarkup()
    for k, r in ROLES.items():
        kb.add(InlineKeyboardButton(r["name"], callback_data=f"role:{k}"))

    await callback.message.answer("Выберите роль:", reply_markup=kb)
    await Creation.choosing_role.set()


@dp.callback_query_handler(lambda c: c.data.startswith("role:"), state=Creation.choosing_role)
async def choose_role(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    await state.update_data(role=ROLES[key])

    data = await state.get_data()

    text = (
        "Персонаж создан (TEST BUILD)\n\n"
        f"Мир: {data['world']['name']}\n"
        f"Предыстория: {data['background']['name']}\n"
        f"Роль: {data['role']['name']}"
    )

    await callback.message.answer(text)
    await Creation.finished.set()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
