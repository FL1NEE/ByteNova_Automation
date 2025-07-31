# -*- coding: utf-8 -*-
import config
import telebot
from keyboard import KEYBOARD
from db_handler import DATABASE
from script_starter import start_bytenova

BOT: str = telebot.TeleBot(
	token = config.BOT_TOKEN,
	num_threads = 2,
	parse_mode = "HTML"
)

@BOT.message_handler(commands = ["start"])
def start(message):
	USER_ID: int = message.chat.id

	BOT.send_message(
		chat_id = USER_ID,
		reply_markup = KEYBOARD.menu_keyboard(), 
		text = "Главное меню!"
	)

@BOT.callback_query_handler(func = lambda call: call.data == "start_bytenova")
def starter(call):
	MSG_ID: int = call.message.message_id
	USER_ID: int = call.message.chat.id

	BOT.answer_callback_query(
		callback_query_id = call.id,
		text = "✅ Запускаю ByteNova Daily!"
	)
	DB: str = DATABASE(
		"servers"
	).get_connect()
	CURSOR: str = DB.cursor()

	for data in CURSOR.execute(f"SELECT * FROM SERVERS"):
		servers: dict = \
		{
			"host": data[0],
			"username": "Administrator",
			"password": data[2]
		}
		start_bytenova(servers)try

if __name__ == '__main__':
	while True:
		try:
			BOT.polling( 
				long_polling_timeout = 3,
				non_stop = True,
				interval = 1,
				timeout = 1
			)
		except Exception as er:print(er)
