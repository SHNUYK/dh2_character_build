import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

from states import Creation
from dice import roll_plus, roll_minus, roll_normal, roll_wounds, roll_blessing
from data import CHARACTERISTICS, HOMEWORLDS, BACKGROUNDS, ROLES

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


# --- команды start / help ---
@dp.message_handler(commands=["start", "wakeup"])
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    kb = InlineKeyboardMarkup()
    for k, w in HOMEWORLDS.items():
        kb.add(InlineKeyboardButton(w["name"], callback_data=f"world:{k}"))
    await message.answer("Выберите родной мир:", reply_markup=kb)
    await Creation.choosing_world.set()


@dp.message_handler(commands=["help"])
async def help_cmd(message: types.Message):
    await message.answer(
        "/start или /wakeup — начать создание персонажа\n"
        "/help — справка\n\n"
        "Создание идёт пошагово через кнопки."
    )


# --- выбор родного мира ---
@dp.callback_query_handler(lambda c: c.data.startswith("world:"), state=Creation.choosing_world)
async def choose_world(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    world = HOMEWORLDS[key]

    # броски характеристик
    plus_rolls = [roll_plus(), roll_plus()]
    minus_roll = roll_minus()
    normal_rolls = [roll_normal() for _ in range(7)]  # 7 обычных включая Влияние

    await state.update_data(
        world=world,
        rolls={
            "plus": plus_rolls,
            "minus": minus_roll,
            "normal": normal_rolls
        },
        assigned={},
        used_values=[]
    )

    # текст результатов бросков
    text = (
        "Броски характеристик выполнены.\n\n"
        f"Плюс: {plus_rolls}\n"
        f"Минус: {minus_roll}\n"
        f"Обычные: {normal_rolls}\n\n"
        "Теперь распределите значения по характеристикам."
    )
    await callback.message.answer(text)

    # показываем выбор характеристик
    kb = InlineKeyboardMarkup()
    for stat in CHARACTERISTICS:
        kb.add(InlineKeyboardButton(stat, callback_data=f"stat:{stat}"))
    await callback.message.answer("Выберите характеристику для назначения значения:", reply_markup=kb)
    await Creation.choosing_background.set()  # временно используем background как следующий шаг


# --- выбор предыстории (stub) ---
@dp.callback_query_handler(lambda c: c.data.startswith("bg:"), state=Creation.choosing_background)
async def choose_bg(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    bg = BACKGROUNDS[key]
    await state.update_data(background=bg)

    kb = InlineKeyboardMarkup()
    for k, r in ROLES.items():
        kb.add(InlineKeyboardButton(r["name"], callback_data=f"role:{k}"))
    await callback.message.answer(f"Предыстория выбрана: {bg['name']}\nБонус: {bg['bonus']}")
    await callback.message.answer("Выберите роль:", reply_markup=kb)
    await Creation.choosing_role.set()


# --- выбор роли (stub) ---
@dp.callback_query_handler(lambda c: c.data.startswith("role:"), state=Creation.choosing_role)
async def choose_role(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    role = ROLES[key]
    await state.update_data(role=role)

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
