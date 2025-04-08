# logger.py

from colorama import Fore, Style
from PySide6.QtGui import QTextCursor

def print_to_terminal(text, color="default"):
    if color == "red":
        print(Fore.RED + text + Style.RESET_ALL)
    elif color == "green":
        print(Fore.GREEN + text + Style.RESET_ALL)
    elif color == "yellow":
        print(Fore.YELLOW + text + Style.RESET_ALL)
    else:
        print(text)


def write_to_output(widget, text):
    widget.moveCursor(QTextCursor.End)
    widget.insertPlainText(text)
    widget.moveCursor(QTextCursor.End)
