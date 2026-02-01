import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

from states import CharacterCreation
from dice import roll_plus, roll_minus, roll_normal
from data import HOMEWORLDS

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=["start", "wakeup"])
async def start_creation(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Введите количество опыта для создаваемого персонажа (целое число больше 0):")
    await CharacterCreation.waiting_for_xp.set()


@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    text = (
        "/start или /wakeup — начать создание персонажа\n"
        "/help — справка\n\n"
        "Создание персонажа идёт пошагово с помощью кнопок."
    )
    await message.answer(text)


@dp.message_handler(state=CharacterCreation.waiting_for_xp)
async def set_xp(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Опыт должен быть целым числом больше 0.")
        return

    await state.update_data(xp=int(message.text))

    kb = InlineKeyboardMarkup()
    for key, world in HOMEWORLDS.items():
        kb.add(InlineKeyboardButton(world["name"], callback_data=f"world:{key}"))

    await message.answer("Выберите родной мир:", reply_markup=kb)
    await CharacterCreation.choosing_homeworld.set()


@dp.callback_query_handler(lambda c: c.data.startswith("world:"), state=CharacterCreation.choosing_homeworld)
async def choose_world(callback: types.CallbackQuery, state: FSMContext):
    world_key = callback.data.split(":")[1]
    world = HOMEWORLDS[world_key]

    plus_values = [roll_plus(), roll_plus()]
    minus_value = roll_minus()
    normal_values = [roll_normal() for _ in range(6)]

    await state.update_data(
        homeworld=world,
        rolls={
            "plus": plus_values,
            "minus": minus_value,
            "normal": normal_values
        },
        characteristics={}
    )

    text = (
        "Броски характеристик выполнены.\n\n"
        f"Значения с плюсом: {plus_values}\n"
        f"Значение с минусом: {minus_value}\n"
        f"Обычные значения: {normal_values}\n\n"
        "Далее вы будете распределять значения по характеристикам."
    )

    await callback.message.answer(text)
    await CharacterCreation.assigning_characteristics.set()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
