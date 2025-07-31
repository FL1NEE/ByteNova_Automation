# -*- coding: utf-8 -*-
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton


class KEYBOARD:
	@staticmethod
	def menu_keyboard():
		MENU: str = InlineKeyboardMarkup()
		MENU.add(
			InlineKeyboardButton(
				text = "Запустить ByteNova",
				callback_data = "start_bytenova"
			)
		)

		return MENU
