# -*- coding: utf-8 -*-
import time
import winrm
from threading import Thread

PATH: str = ""

GOOD: int = 0
ERROR: int = 0

def start_bytenova(server: dict) -> str:
	session = winrm.Session(
		f"http://{server["host"]}:5985/wsman",
		auth = \
		(
			server["username"],
			server["password"]
		)
	)
	cmd_script = "cd Desktop && cd 1040Anti && python main.py 1"

	result = session.run_cmd(cmd_script)
	output = result.std_out.decode('utf-8', errors='replace') if isinstance(result.std_out, bytes) else result.std_out
	error = result.std_err.decode('utf-8', errors='replace') if isinstance(result.std_err, bytes) else result.std_err
	print(f"Output: {output}")
	print(f"Error: {error}")
