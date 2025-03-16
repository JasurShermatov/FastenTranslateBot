from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from utils.database.db import DataBase

# DataBase obyektini chaqiramiz
db = DataBase()


def chunk_list(values, chunk_size=1):
    """Ro'yxatni har bir qator uchun chunk_size ta elementga bo'lish."""
    return [values[i : i + chunk_size] for i in range(0, len(values), chunk_size)]


async def get_channel_keyboard(missing_channels: list = None) -> InlineKeyboardMarkup:
    """Foydalanuvchi obuna bo'lmagan kanallar uchun klaviatura yaratish."""

    # Agar missing_channels berilmagan bo'lsa, barcha kanallarni olish
    if missing_channels is None:
        channels = await db.get_all_subscriptions()
    else:
        channels = missing_channels

    # Agar kanallar bo'lmasa, xabar qaytarish
    if not channels:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Barcha kanallarga obuna bo'lgansiz",
                        callback_data="all_subscribed",
                    )
                ]
            ]
        )

    # Faqat obuna bo'lmagan kanallar uchun tugmalar yaratish
    buttons = [
        InlineKeyboardButton(text=f"{channel['name']}", url=channel["link"])
        for channel in channels
    ]

    # Tugmalarni 1 qatorga joylashtiramiz
    inline_buttons = chunk_list(buttons, chunk_size=1)

    # "♻️ TEKSHIRISH" tugmasini qo'shamiz
    inline_buttons.append(
        [
            InlineKeyboardButton(
                text="✅OBUNA BO'LDIM", callback_data="check_subscription"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=inline_buttons)



from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class get_user_kb:
    @staticmethod
    async def get_main_keyboard():
        """Asosiy menyu uchun inline keyboard"""
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📚 Cambridge Translate", callback_data="translate")],
                [InlineKeyboardButton(text="🌐 Google Translate", web_app=WebAppInfo(url="https://translate.google.com"))]
                # Boshqa tugmalarni shu yerga qo'shishingiz mumkin
            ]
        )
        return keyboard

    @staticmethod
    async def get_back_keyboard():
        """Orqaga qaytish uchun keyboard"""
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Asosiy menyuga qaytish", callback_data="back_to_main")],
            ]
        )
        return keyboard

