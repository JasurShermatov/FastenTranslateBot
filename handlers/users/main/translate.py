
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from utils.translate_api import CambridgeDictionary
from keyboards.inline.user import get_user_kb
from utils.database.db import DataBase

# Logger
logger = logging.getLogger(__name__)

# Router yaratish
router = Router()
cambridge_api = CambridgeDictionary()
db = DataBase()


# Translation states
class TranslateStates(StatesGroup):
    waiting_for_word = State()


# Translate buyrug'i
@router.message(Command("translate"))
async def translate_command(message: Message, state: FSMContext):
    await state.set_state(TranslateStates.waiting_for_word)
    await message.answer(
        "<b>📖 🔎 Cambridge Dictionary orqali qanday ma'lumot olishingiz mumkin:</b>\n\n"
        "🌟 <b>So'z ma'nosi:</b> So'zni yuboring va uning aniq ma'nosini oling.\n"
        "🔊 <b>Talaffuz:</b> So'zning to'g'ri talaffuzini britancha va amerikalikcha tinglang.\n"
        "📝 <b>Misollar:</b> So'zning kontekstda ishlatilishini ko'ring.\n"
        "🌍 <b>Sinonim va Antonimlar:</b> So'zning o'xshash va qarama-qarshi ma'nolarini biling.\n\n"
        "📌 <b>Misol:</b> <i>“run”</i> → <b>yugurmoq</b> 🔊 (Talaffuzni tinglash)\n\n"
        "👉 <b>So'zni yozing va Cambridge Dictionary orqali ma'lumot oling!</b> 🚀",
        parse_mode="HTML",
        reply_markup=await get_user_kb.get_back_keyboard()
    )


# Translate callback
@router.callback_query(F.data == "translate")
async def start_translation(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TranslateStates.waiting_for_word)
    await callback.message.answer(
        "<b>📚 Cambridge Dictionary imkoniyatlari:</b>\n"
        "🌟 <b>Ma'no:</b> So'zni yuboring va aniq ma'nosini oling.\n"
        "🔊 <b>Talaffuz:</b> Britancha va amerikalikcha tinglang.\n"
        "👉 So'zni yozing va ma'lumot oling! 🚀",
           parse_mode="HTML",
        reply_markup=await get_user_kb.get_back_keyboard()
    )
    await callback.answer()


# Orqaga qaytish
@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    from handlers.users.main.start import show_main_menu
    await state.clear()
    await callback.message.delete()
    await show_main_menu(callback.message)
    await callback.answer()


# So'z qabul qilish va tarjima qilish
@router.message(StateFilter(TranslateStates.waiting_for_word))
async def process_word(message: Message, state: FSMContext):
    user_id = message.from_user.id
    word = message.text.strip()

    # Statistika uchun so'rov sonini oshirish
    await db.update_user_activity(user_id=user_id)

    # Xabar yuborish - yuklanmoqda
    progress_msg = await message.answer(f"🔍 <b>{word}</b> so'zi qidirilmoqda...")

    # Cambridge Dictionary dan ma'lumot olish
    result = await cambridge_api.get_word_info(word)

    if not result['success']:
        await progress_msg.edit_text(
            f"❌ {result.get('error', 'Xatolik yuz berdi')}",
            reply_markup=await get_user_kb.get_back_keyboard()
        )
        return

    # Natijalarni formatlab chiqarish
    text = f"📕 <b>{word.upper()}</b>\n\n"

    # Ma'nolarini qo'shish
    if result['definitions']:
        text += "<b>Ma'nosi:</b>\n"
        for i, definition in enumerate(result['definitions'], 1):
            text += f"{i}. {definition}\n"
    else:
        text += "⚠️ Bu so'z uchun ma'no topilmadi.\n"

    # Audio havolalarini qo'shish
    text += "\n<b>🔊 Talaffuz:</b>\n"
    if result['pronunciations']['uk'] or result['pronunciations']['us']:
        text += "Audio fayllar yuborilmoqda..."
    else:
        text += "⚠️ Bu so'z uchun audio talaffuz topilmadi."

    # Javobni yuborish
    await progress_msg.edit_text(
        text,
        reply_markup=await get_user_kb.get_back_keyboard(),
        disable_web_page_preview=True
    )

    # Agar audio mavjud bo'lsa, ularni yuborish
    try:
        if result['pronunciations']['uk']:
            await message.answer_audio(
                result['pronunciations']['uk'],
                caption="🇬🇧 Britaniya talaffuzi"
            )

        if result['pronunciations']['us']:
            await message.answer_audio(
                result['pronunciations']['us'],
                caption="🇺🇸 Amerika talaffuzi"
            )
    except Exception as e:
        logger.error(f"Audio yuborishda xatolik: {str(e)}")
        await message.answer(
            "⚠️ Audio fayllarni yuborishda xatolik yuz berdi.",
            reply_markup=await get_user_kb.get_back_keyboard()
        )