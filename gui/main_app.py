import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, 
    QMessageBox, QFileDialog, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt

# Import the data processing function from the data_processor module.
# Assumes data_processor.py is in the 'core' folder.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from data_processor import process_ai_data

# Import translations
from translations import TRANSLATIONS, LANGUAGES

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_lang = "en" # Default language is English
        self.setup_ui()
        self.update_language() # Set initial language and text

    def tr(self, key):
        """Translates a given key to the current language."""
        return TRANSLATIONS.get(key, {}).get(self.current_lang, key)

    def setup_ui(self):
        main_layout = QGridLayout()

        # 1. Language Selection
        language_label = QLabel(self.tr("Language:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(sorted(LANGUAGES.keys()))
        self.language_combo.setCurrentText("English")
        self.language_combo.currentIndexChanged.connect(self.update_language)

        # 2. Input File Path Widgets
        self.input_label = QLabel(self.tr("Input File Path:"))
        self.input_entry = QLineEdit()
        self.input_entry.setPlaceholderText(self.tr("e.g. data/input_data.txt"))
        self.input_browse_button = QPushButton(self.tr("Browse"))
        self.input_browse_button.clicked.connect(lambda: self.browse_file(self.input_entry, is_input=True))

        # 3. Output File Path Widgets
        self.output_label = QLabel(self.tr("Output File Path:"))
        self.output_entry = QLineEdit()
        self.output_entry.setPlaceholderText(self.tr("e.g. data/output_data.xlsx"))
        self.output_browse_button = QPushButton(self.tr("Browse"))
        self.output_browse_button.clicked.connect(lambda: self.browse_file(self.output_entry, is_input=False))

        # 4. Number of Columns Widgets
        self.columns_label = QLabel(self.tr("Number of Columns:"))
        self.columns_entry = QLineEdit()
        self.columns_entry.setPlaceholderText(self.tr("e.g. 8"))

        # 5. Extra Delimiters Checkbox
        self.ignore_checkbox = QCheckBox(self.tr("Ignore extra delimiters"))
        
        # 6. Process Button
        self.process_button = QPushButton(self.tr("Process Data"))
        self.process_button.clicked.connect(self.process_data_from_gui)

        # 7. Author Info
        self.author_label = QLabel(self.tr("Developed by Ahmadreza Haj Talebi"))
        self.author_label.setStyleSheet("color: gray; font-size: 10px;")

        # Adding widgets to the grid layout for symmetry
        main_layout.addWidget(language_label, 0, 0)
        main_layout.addWidget(self.language_combo, 0, 1, 1, 2)
        
        main_layout.addWidget(self.input_label, 1, 0)
        main_layout.addWidget(self.input_entry, 1, 1)
        main_layout.addWidget(self.input_browse_button, 1, 2)

        main_layout.addWidget(self.output_label, 2, 0)
        main_layout.addWidget(self.output_entry, 2, 1)
        main_layout.addWidget(self.output_browse_button, 2, 2)

        main_layout.addWidget(self.columns_label, 3, 0)
        main_layout.addWidget(self.columns_entry, 3, 1)

        main_layout.addWidget(self.ignore_checkbox, 4, 0, 1, 3) # Span across all 3 columns
        main_layout.addWidget(self.process_button, 5, 0, 1, 3) # Span across all 3 columns
        main_layout.addWidget(self.author_label, 6, 0, 1, 3, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)
        self.setWindowTitle(self.tr("Research Data Processor"))
        self.resize(650, 300) # Increased height to accommodate the new checkbox
    
    def update_language(self):
        """Updates all UI text based on the selected language."""
        selected_language = self.language_combo.currentText()
        self.current_lang = LANGUAGES.get(selected_language, "en")
        
        # Update window title
        self.setWindowTitle(self.tr("Research Data Processor"))
        
        # Update labels
        self.input_label.setText(self.tr("Input File Path:"))
        self.input_entry.setPlaceholderText(self.tr("e.g. data/input_data.txt"))
        self.output_label.setText(self.tr("Output File Path:"))
        self.output_entry.setPlaceholderText(self.tr("e.g. data/output_data.xlsx"))
        self.columns_label.setText(self.tr("Number of Columns:"))
        self.columns_entry.setPlaceholderText(self.tr("e.g. 8"))
        self.ignore_checkbox.setText(self.tr("Ignore extra delimiters"))
        self.input_browse_button.setText(self.tr("Browse"))
        self.output_browse_button.setText(self.tr("Browse"))
        self.process_button.setText(self.tr("Process Data"))
        self.author_label.setText(self.tr("Developed by Ahmadreza Haj Talebi"))
    
    def browse_file(self, line_edit_widget, is_input):
        """Opens a file dialog for selecting input or output files."""
        if is_input:
            dialog_title = self.tr("Select Input File")
            file_filters = self.tr("Text Files (*.txt);;CSV Files (*.csv);;All Files (*)")
            file_path, _ = QFileDialog.getOpenFileName(self, dialog_title, "", file_filters)
        else:
            dialog_title = self.tr("Select Output Path")
            file_filters = self.tr("Excel Files (*.xlsx)")
            file_path, _ = QFileDialog.getSaveFileName(self, dialog_title, "", file_filters)
        
        if file_path:
            line_edit_widget.setText(file_path)

    def process_data_from_gui(self):
        """Processes user input, calls the main data processing function, and displays warnings."""
        input_path = self.input_entry.text()
        output_path = self.output_entry.text()
        columns_text = self.columns_entry.text()
        ignore_flag = self.ignore_checkbox.isChecked()

        if not input_path or not output_path or not columns_text:
            QMessageBox.warning(self, self.tr("Input Error"), self.tr("All fields must be filled out."))
            return

        try:
            num_columns = int(columns_text)
            if num_columns <= 0:
                 QMessageBox.warning(self, self.tr("Input Error"), self.tr("Number of columns must be a positive integer."))
                 return
        except ValueError:
            QMessageBox.warning(self, self.tr("Input Error"), self.tr("Number of columns must be a valid integer."))
            return

        # Call the data processing function with the new flag
        df, warnings = process_ai_data(input_path, output_path, num_columns, ignore_extra_delimiters=ignore_flag)
        
        if warnings:
            QMessageBox.information(self, self.tr("Processing Report"), "\n".join(warnings))

        if df is not None:
            QMessageBox.information(self, self.tr("Success"), self.tr("Data processing complete!"))


if __name__ == "__main__":
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())