# command_runner.py

import subprocess
import threading
from datetime import datetime
from config import WORKING_DIR
from utils.logger import print_to_terminal

def execute_command(cmd, output_callback, terminal_callback):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"[{timestamp}] $ {cmd}\n"
    output_callback(header)
    terminal_callback(header, color="yellow")

    try:
        process = subprocess.run(
            cmd,
            shell=True,
            cwd=WORKING_DIR,
            capture_output=True,
            text=True
        )
        if process.stdout:
            output_callback(process.stdout)
            terminal_callback(process.stdout, color="green")
        if process.stderr:
            error_message = f"Error: {process.stderr}\n"
            output_callback(error_message)
            terminal_callback(error_message, color="red")
        if process.returncode != 0:
            problem = "Houston, we have a problem!\n"
            output_callback(problem)
            terminal_callback(problem, color="red")
    except Exception as e:
        error_message = f"Exception: {str(e)}\n"
        output_callback(error_message)
        terminal_callback(error_message, color="red")

    separator = "-" * 40 + "\n"
    output_callback(separator)
    terminal_callback(separator)

def run_command(command, output_callback, terminal_callback):
    thread = threading.Thread(target=execute_command, args=(command, output_callback, terminal_callback))
    thread.start()
