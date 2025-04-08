# main_window.py

import webbrowser
from PySide6.QtWidgets import (QMainWindow, QTextEdit, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QProgressBar, QLineEdit)
from PySide6.QtCore import Qt, QTimer
from PySide6 import QtGui
from ui.styles import DEFAULT_STYLE
from commands.command_runner import run_command
from monitors import system_monitor, docker_monitor
from utils.logger import print_to_terminal, write_to_output

class OperationsCommandCenter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mission Control Center")
        self.setGeometry(100, 100, 900, 600)
        self.gpu_bars = []
        self.setup_ui()
        self.set_default_style()
        self.start_system_monitor()
        self.start_docker_monitor()

    def setup_ui(self):
        main_widget = QWidget()
        outer_layout = QHBoxLayout()

        # Left side: Output and system monitor
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # Text output area
        self.output_text = QTextEdit()
        self.output_text.setFontPointSize(10)
        self.output_text.setReadOnly(True)
        left_layout.addWidget(self.output_text, stretch=1)

        # Resource monitor layout
        resource_layout = QVBoxLayout()
        # CPU usage
        self.cpu_label = QLabel("CPU Load:")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        resource_layout.addWidget(self.cpu_label)
        resource_layout.addWidget(self.cpu_progress)
        # Memory usage
        self.mem_label = QLabel("Memory Usage:")
        self.mem_progress = QProgressBar()
        self.mem_progress.setRange(0, 100)
        resource_layout.addWidget(self.mem_label)
        resource_layout.addWidget(self.mem_progress)
        # GPU usage
        self.gpu_label = QLabel("GPU Usage:")
        resource_layout.addWidget(self.gpu_label)
        gpu_data = system_monitor.get_gpu_usage()
        if gpu_data:
            for gpu in gpu_data:
                gpu_bar = QProgressBar()
                gpu_bar.setRange(0, 100)
                gpu_bar.setFormat(f"GPU {gpu['index']}")
                resource_layout.addWidget(gpu_bar)
                self.gpu_bars.append(gpu_bar)
        else:
            resource_layout.addWidget(QLabel("No GPU detected"))

        left_layout.addLayout(resource_layout)
        left_widget.setLayout(left_layout)

        # Right side: Command Buttons and additional controls
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        commands = [
            ("Run Docker", r'"C:\Program Files\Docker\Docker\frontend\Docker Desktop.exe"'),
            ("Docker Compose Down", "docker compose down"),
            ("Docker Compose Up", "docker compose up -d"),
            ("Ollama List", "ollama list"),
            ("PM2 Restart All", "pm2 restart all")
        ]
        for label, cmd in commands:
            if label == "Run Docker":
                h_layout = QHBoxLayout()
                docker_button = QPushButton(label)
                docker_button.clicked.connect(lambda checked, c=cmd: run_command(c, self.append_output, print_to_terminal))
                h_layout.addWidget(docker_button)
                self.docker_led = QLabel()
                self.docker_led.setFixedSize(20, 20)
                self.docker_led.setStyleSheet("background-color: red; border-radius: 10px;")
                h_layout.addWidget(self.docker_led)
                h_layout.addStretch()
                right_layout.addLayout(h_layout)
            else:
                button = QPushButton(label)
                button.clicked.connect(lambda checked, c=cmd: run_command(c, self.append_output, print_to_terminal))
                right_layout.addWidget(button)
        
        ollama_button = QPushButton("Open Ollama Search")
        ollama_button.clicked.connect(self.open_ollama)
        right_layout.addWidget(ollama_button)

        # Model installer section
        model_label = QLabel("Enter model name:")
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("e.g., ollama run command-a")
        install_button = QPushButton("Install Model")
        install_button.clicked.connect(self.install_model)
        right_layout.addWidget(model_label)
        right_layout.addWidget(self.model_input)
        right_layout.addWidget(install_button)

        url_button = QPushButton("Open ChatBot")
        url_button.clicked.connect(self.open_url)
        right_layout.addWidget(url_button)

        right_layout.addStretch()
        right_widget.setLayout(right_layout)

        outer_layout.addWidget(left_widget, stretch=3)
        outer_layout.addWidget(right_widget, stretch=1)
        main_widget.setLayout(outer_layout)
        self.setCentralWidget(main_widget)

    def set_default_style(self):
        self.setStyleSheet(DEFAULT_STYLE)

    def append_output(self, text):
        write_to_output(self.output_text, text)

    def open_url(self):
        webbrowser.open("http://localhost:3080/")

    def open_ollama(self):
        webbrowser.open("https://ollama.com/search")

    def install_model(self):
        model_name = self.model_input.text().strip()
        if model_name:
            run_command(model_name, self.append_output, print_to_terminal)
        else:
            self.append_output("No model name provided.\n")
            print_to_terminal("No model name provided.\n", color="red")

    def start_system_monitor(self):
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_resource_usage)
        self.monitor_timer.start(2000)

    def update_resource_usage(self):
        cpu = system_monitor.get_cpu_usage()
        self.cpu_progress.setValue(int(cpu))
        self.cpu_label.setText(f"CPU Load: {cpu:.2f}%")

        mem = system_monitor.get_memory_usage()
        self.mem_progress.setValue(int(mem))
        self.mem_label.setText(f"Memory Usage: {mem:.2f}%")

        gpu_data = system_monitor.get_gpu_usage()
        if self.gpu_bars and gpu_data:
            for i, gpu in enumerate(gpu_data):
                usage = gpu['load']
                self.gpu_bars[i].setValue(int(usage))
                self.gpu_bars[i].setFormat(f"GPU {gpu['index']}: {usage:.2f}% (Used: {gpu['memory_used']} MB)")

    def start_docker_monitor(self):
        self.docker_timer = QTimer()
        self.docker_timer.timeout.connect(self.update_docker_led)
        self.docker_timer.start(2000)

    def update_docker_led(self):
        if docker_monitor.is_docker_running():
            self.docker_led.setStyleSheet("background-color: green; border-radius: 10px;")
        else:
            self.docker_led.setStyleSheet("background-color: red; border-radius: 10px;")
