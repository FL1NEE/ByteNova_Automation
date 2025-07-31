# -*- coding: utf-8 -*-
from sqlite3 import connect

class DATABASE(object):
	def __init__(self, FILENAME: str) -> str:
		self.FILENAME: str = FILENAME

	def get_connect(self):
		return connect(f"{self.FILENAME}.db", check_same_thread = False)
