"""Хендлер бота: кнопка «Играть» открывает Mini App (FR-001)."""

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from src.config import settings

router = Router(name="play")

PLAY_BUTTON_TEXT = "🎁 Играть"


def _play_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=PLAY_BUTTON_TEXT,
                    web_app=WebAppInfo(url=settings.mini_app_url),
                )
            ]
        ]
    )


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        "Добро пожаловать в магазин электроники! Сыграй в скретч-карту и получи промокод на скидку.",
        reply_markup=_play_keyboard(),
    )


@router.message(F.text == PLAY_BUTTON_TEXT)
async def handle_play_text(message: Message) -> None:
    await message.answer("Открой карту в мини-приложении ниже:", reply_markup=_play_keyboard())
