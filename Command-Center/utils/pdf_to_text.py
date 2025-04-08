import sys, os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget,
    QProgressBar, QFileDialog, QMessageBox, QTextEdit, QComboBox, QHBoxLayout
)
from PySide6.QtCore import QThread, Signal
import pdfplumber

# -------------------------
# Worker for Single PDF Extraction
# -------------------------
class SingleExtractionWorker(QThread):
    finished = Signal(str)      # Emitted when extraction is complete; returns the content string.
    progress = Signal(int)      # Emits progress percentage (0-100).
    error = Signal(str)         # Emits error messages.
    
    def __init__(self, pdf_path, mode):
        super().__init__()
        self.pdf_path = pdf_path
        self.mode = mode  # Expected values: "Text Only", "Tables Only", "Both"
    
    def run(self):
        try:
            from tqdm import tqdm  # Console progress
            content = ""
            with pdfplumber.open(self.pdf_path) as pdf:
                n_pages = len(pdf.pages)
                # Iterate with tqdm for console progress
                for i, page in enumerate(tqdm(pdf.pages, total=n_pages, desc="Extracting pages")):
                    # Extract text if mode is Text Only or Both
                    if self.mode in ("Text Only", "Both"):
                        page_text = page.extract_text()
                        if page_text:
                            content += f"--- Page {i+1} Text ---\n{page_text}\n"
                    # Extract tables if mode is Tables Only or Both
                    if self.mode in ("Tables Only", "Both"):
                        tables = page.extract_tables()
                        if tables:
                            for j, table in enumerate(tables):
                                content += f"Page {i+1} - Table {j+1}:\n"
                                for row in table:
                                    # Join row items with comma
                                    row_str = ",".join([str(cell) if cell is not None else "" for cell in row])
                                    content += row_str + "\n"
                                content += "\n"
                    progress_value = int(((i + 1) / n_pages) * 100)
                    self.progress.emit(progress_value)
            self.finished.emit(content)
        except Exception as e:
            self.error.emit(str(e))

# -------------------------
# Worker for Batch PDF Extraction
# -------------------------
class BatchExtractionWorker(QThread):
    progress = Signal(int)      # Overall progress (0-100) across all files.
    finished = Signal()         # Emitted when batch processing is complete.
    error = Signal(str)         # Emits error messages.
    
    def __init__(self, folder_path, mode, output_folder):
        super().__init__()
        self.folder_path = folder_path
        self.mode = mode            # "Text Only", "Tables Only", or "Both"
        self.output_folder = output_folder
    
    def run(self):
        try:
            from tqdm import tqdm  # Console progress for batch processing
            pdf_files = [f for f in os.listdir(self.folder_path) if f.lower().endswith('.pdf')]
            total_files = len(pdf_files)
            if total_files == 0:
                self.error.emit("No PDF files found in the selected folder.")
                return
            for idx, pdf_file in enumerate(tqdm(pdf_files, total=total_files, desc="Batch Processing")):
                pdf_path = os.path.join(self.folder_path, pdf_file)
                content = ""
                with pdfplumber.open(pdf_path) as pdf:
                    n_pages = len(pdf.pages)
                    for i, page in enumerate(pdf.pages):
                        if self.mode in ("Text Only", "Both"):
                            page_text = page.extract_text()
                            if page_text:
                                content += f"--- Page {i+1} Text ---\n{page_text}\n"
                        if self.mode in ("Tables Only", "Both"):
                            tables = page.extract_tables()
                            if tables:
                                for j, table in enumerate(tables):
                                    content += f"Page {i+1} - Table {j+1}:\n"
                                    for row in table:
                                        row_str = ",".join([str(cell) if cell is not None else "" for cell in row])
                                        content += row_str + "\n"
                                    content += "\n"
                # Save output using the same base name as the PDF (with .txt extension)
                output_file_name = os.path.splitext(pdf_file)[0] + ".txt"
                output_path = os.path.join(self.output_folder, output_file_name)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)
                progress_value = int(((idx + 1) / total_files) * 100)
                self.progress.emit(progress_value)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

# -------------------------
# Main GUI Window
# -------------------------
class PDFConverterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF to Text Converter")
        self.single_worker = None
        self.batch_worker = None
        self.setup_ui()
    
    def setup_ui(self):
        # Main layout and container widget
        layout = QVBoxLayout()
        
        title_label = QLabel("<h2>PDF to Text Converter</h2>")
        layout.addWidget(title_label)
        
        # Mode selection: Text Only, Tables Only, or Both
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Extraction Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Text Only", "Tables Only", "Both"])
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)
        
        # Buttons for Single PDF and Batch Processing
        button_layout = QHBoxLayout()
        self.single_btn = QPushButton("Convert Single PDF")
        self.single_btn.clicked.connect(self.select_single_pdf)
        self.batch_btn = QPushButton("Batch Process Folder")
        self.batch_btn.clicked.connect(self.select_folder)
        button_layout.addWidget(self.single_btn)
        button_layout.addWidget(self.batch_btn)
        layout.addLayout(button_layout)
        
        # Progress bar (for either single or batch mode)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Preview text area for single file extraction
        self.preview = QTextEdit()
        self.preview.setPlaceholderText("Extracted content preview will appear here...")
        layout.addWidget(self.preview)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    # ----- Single PDF Conversion -----
    def select_single_pdf(self):
        pdf_path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if pdf_path:
            self.preview.clear()
            self.progress_bar.setValue(0)
            mode = self.mode_combo.currentText()
            self.single_worker = SingleExtractionWorker(pdf_path, mode)
            self.single_worker.progress.connect(self.progress_bar.setValue)
            self.single_worker.finished.connect(self.on_single_finished)
            self.single_worker.error.connect(self.on_error)
            self.single_worker.start()
    
    def on_single_finished(self, content):
        # Display the extracted content in the preview area
        self.preview.setPlainText(content)
        # Ask user if they wish to save the content
        save_choice = QMessageBox.question(
            self, "Save Output", "Extraction complete. Would you like to save the result?",
            QMessageBox.Yes | QMessageBox.No
        )
        if save_choice == QMessageBox.Yes:
            output_path, _ = QFileDialog.getSaveFileName(self, "Save Output As", "", "Text Files (*.txt)")
            if output_path:
                try:
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    QMessageBox.information(self, "Saved", f"Output saved to:\n{output_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")
    
    # ----- Batch Processing -----
    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder Containing PDFs")
        if folder_path:
            # Ask for output folder to store extracted files
            output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
            if not output_folder:
                return
            self.progress_bar.setValue(0)
            mode = self.mode_combo.currentText()
            self.batch_worker = BatchExtractionWorker(folder_path, mode, output_folder)
            self.batch_worker.progress.connect(self.progress_bar.setValue)
            self.batch_worker.finished.connect(self.on_batch_finished)
            self.batch_worker.error.connect(self.on_error)
            self.batch_worker.start()
    
    def on_batch_finished(self):
        QMessageBox.information(self, "Batch Completed", "All PDFs in the folder have been processed.")
    
    # ----- Error Handling -----
    def on_error(self, error_message):
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_message}")

# -------------------------
# Main Execution
# -------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFConverterWindow()
    window.resize(600, 500)
    window.show()
    sys.exit(app.exec())
