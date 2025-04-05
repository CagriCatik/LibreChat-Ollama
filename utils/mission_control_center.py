import sys
import subprocess
import threading
import os
import webbrowser
import time
from pathlib import Path
from psutil import cpu_percent, virtual_memory
from datetime import datetime
from queue import Queue
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6 import QtGui
import GPUtil
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

WORKING_DIR = os.path.join(os.getcwd(), "Frontend")

class OperationsCommandCenter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mission Control Center")
        self.setGeometry(100, 100, 900, 600)
        
        self.setup_ui()
        self.configure_connections()
        self.set_default_style()
        self.start_system_monitor()

    def setup_ui(self):
        main_widget = QWidget()
        outer_layout = QHBoxLayout()
        
        # Left side: Output and system monitor
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        self.output_text = QTextEdit()
        self.output_text.setFontPointSize(10)
        self.output_text.setReadOnly(True)
        left_layout.addWidget(self.output_text, stretch=1)
        
        self.cpu_usage_label = QLabel("CPU Load: 0.00%")
        self.mem_usage_label = QLabel("Memory Usage: 0.00%")
        self.gpu_usage_label = QLabel("GPU Usage: N/A")
        
        monitor_layout = QHBoxLayout()
        monitor_layout.addWidget(self.cpu_usage_label)
        monitor_layout.addWidget(self.mem_usage_label)
        monitor_layout.addWidget(self.gpu_usage_label)
        
        monitor_widget = QWidget()
        monitor_widget.setLayout(monitor_layout)
        left_layout.addWidget(monitor_widget)
        
        left_widget.setLayout(left_layout)
        
        # Right side: Command Buttons
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        # Added an extra button for running Docker Desktop.
        commands = [
            ("Run Docker", r'"C:\Program Files\Docker\Docker\frontend\Docker Desktop.exe"'),
            ("Docker Compose Down", "docker compose down"),
            ("Docker Compose Up", "docker compose up -d"),
            ("Ollama List", "ollama list"),
            ("PM2 Restart All", "pm2 restart all")
        ]
        
        for label, cmd in commands:
            button = QPushButton(label)
            right_layout.addWidget(button)
            button.clicked.connect(lambda checked, cmd=cmd: self.run_command(cmd))
        
        # Open ChatBot URL button
        url_button = QPushButton("Open ChatBot")
        right_layout.addWidget(url_button)
        url_button.clicked.connect(self.open_url)
        
        right_layout.addStretch()
        right_widget.setLayout(right_layout)
        
        outer_layout.addWidget(left_widget, stretch=3)
        outer_layout.addWidget(right_widget, stretch=1)
        
        main_widget.setLayout(outer_layout)
        self.setCentralWidget(main_widget)

    def configure_connections(self):
        pass

    def set_default_style(self):
        style = """
            QPushButton {
                padding: 8px;
                margin: 4px;
                border-radius: 4px;
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QTextEdit {
                font-family: monospace;
                font-size: 10pt;
            }
        """
        self.setStyleSheet(style)

    def run_command(self, command):
        thread = threading.Thread(target=self.execute_command, args=(command,))
        thread.start()

    def execute_command(self, cmd):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        command_header = f"[{timestamp}] $ {cmd}\n"
        self.write_to_output(command_header)
        self.print_to_terminal(command_header, color='yellow')
        
        try:
            process = subprocess.run(
                cmd,
                shell=True,
                cwd=WORKING_DIR,
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.stdout:
                self.write_to_output(process.stdout)
                self.print_to_terminal(process.stdout, color='green')
            if process.stderr:
                error_text = f"Error: {process.stderr}\n"
                self.write_to_output(error_text)
                self.print_to_terminal(error_text, color='red')
            
            if process.returncode != 0 or process.stderr:
                problem_text = "Houston, we have a problem!\n"
                self.write_to_output(problem_text)
                self.print_to_terminal(problem_text, color='red')
                
        except Exception as e:
            exception_text = f"Exception: {str(e)}\n"
            self.write_to_output(exception_text)
            self.print_to_terminal(exception_text, color='red')
            problem_text = "Houston, we have a problem!\n"
            self.write_to_output(problem_text)
            self.print_to_terminal(problem_text, color='red')

        self.write_to_output("-" * 40 + "\n")
        self.print_to_terminal("-" * 40 + "\n")

    def write_to_output(self, text):
        self.output_text.moveCursor(QtGui.QTextCursor.End)
        self.output_text.insertPlainText(text)
        self.output_text.moveCursor(QtGui.QTextCursor.End)

    def print_to_terminal(self, text, color='default'):
        if color == 'red':
            print(Fore.RED + text + Style.RESET_ALL)
        elif color == 'green':
            print(Fore.GREEN + text + Style.RESET_ALL)
        elif color == 'yellow':
            print(Fore.YELLOW + text + Style.RESET_ALL)
        else:
            print(text)

    def open_url(self):
        webbrowser.open("http://localhost:3080/")

    def start_system_monitor(self):
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_resource_usage)
        self.monitor_timer.start(2000)

    def update_resource_usage(self):
        cpu = cpu_percent(interval=0.1)
        mem = virtual_memory().percent
        self.set_cpu_usage(cpu)
        self.set_mem_usage(mem)
        self.update_gpu_usage()

    def set_cpu_usage(self, usage):
        self.cpu_usage_label.setText(f"CPU Load: {usage:.2f}%")

    def set_mem_usage(self, usage):
        self.mem_usage_label.setText(f"Memory Usage: {usage:.2f}%")

    def update_gpu_usage(self):
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_info = ""
                for i, gpu in enumerate(gpus):
                    usage_percent = gpu.load * 100
                    gpu_info += f"GPU {i}: {usage_percent:.2f}% (Used: {gpu.memoryUsed} MB)  "
                self.gpu_usage_label.setText(gpu_info)
            else:
                self.gpu_usage_label.setText("GPU Not Found")
        except Exception as e:
            self.gpu_usage_label.setText("GPU monitoring error")

def main():
    app = QApplication(sys.argv)
    window = OperationsCommandCenter()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
