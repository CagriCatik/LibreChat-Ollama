# styles.py

DEFAULT_STYLE = """
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
    QProgressBar {
        border: 2px solid grey;
        border-radius: 5px;
        text-align: center;
        height: 30px;
    }
    QProgressBar::chunk {
        background-color: #4CAF50;
        width: 20px;
    }
    QLineEdit {
        padding: 6px;
        border: 2px solid grey;
        border-radius: 4px;
    }
"""
