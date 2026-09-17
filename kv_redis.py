import time, redis
from datetime import datetime
from os import environ

_key_state_text = "state_text_value"
_key_last_change = "state_text_last_change"
_key_history = "history"

class Bridge:
	def __init__(self, default_text):
		self.rd = redis.from_url(environ["KV_URL"])
		if self.rd.get(_key_state_text) is None:
			self.rd.set(_key_state_text, default_text)
		if self.rd.get(_key_last_change) is None:
			self.rd.set(_key_last_change, "0.0")
		if self.rd.get(_key_history) is None:
			self.rd.set(_key_history, "")
	
	def get_text(self):
		return self.rd.get(_key_state_text).decode()
	
	def get_last_change(self):
		return float(self.rd.get(_key_last_change).decode())
	
	def set_text_and_update_time(self, text):
		self.rd.set(_key_state_text, text)
		self.rd.set(_key_last_change, str(time.time()))

		now = datetime.now()
		dt = now.strftime("%d.%m.%Y, %H:%M:%S")
		history = self.rd.get(_key_history).decode()
		history += f"[{dt}] {text}\n"
		self.rd.set(_key_history, history)

	def get_history(self):
		return self.rd.get(_key_history).decode().splitlines()
