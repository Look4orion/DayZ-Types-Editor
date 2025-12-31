"""
File Loading Error Dialog
Shows summary of files that failed to load with reasons
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QTextEdit)
from PyQt5.QtCore import Qt
from typing import List, Dict

class FileErrorDialog(QDialog):
    def __init__(self, parent, errors: List[Dict[str, str]], total_files: int, loaded_files: int):
        super().__init__(parent)
        self.errors = errors
        self.total_files = total_files
        self.loaded_files = loaded_files
        
        self.setWindowTitle("File Loading Errors")
        self.setModal(True)
        self.setMinimumSize(800, 500)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Apply dark theme to dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #cccccc;
            }
            QLabel {
                color: #cccccc;
            }
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #252526;
                color: #cccccc;
                gridline-color: #333;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #333;
                padding: 4px;
            }
            QTextEdit {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #333;
            }
        """)
        
        # Summary
        summary_text = f"Loaded {self.loaded_files} of {self.total_files} files successfully."
        if self.errors:
            summary_text += f" {len(self.errors)} file(s) failed to load."
        
        summary_label = QLabel(summary_text)
        summary_label.setStyleSheet("font-size: 12px; font-weight: bold; padding: 10px; color: #cccccc;")
        layout.addWidget(summary_label)
        
        if self.errors:
            # Error table
            error_label = QLabel("Files with errors (fix these in your mission folder):")
            error_label.setStyleSheet("font-weight: bold; padding: 5px; color: #cccccc;")
            layout.addWidget(error_label)
            
            self.error_table = QTableWidget()
            self.error_table.setColumnCount(3)
            self.error_table.setHorizontalHeaderLabels(["File", "Error Type", "Details"])
            self.error_table.setRowCount(len(self.errors))
            
            # Configure table
            self.error_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.error_table.setSelectionBehavior(QTableWidget.SelectRows)
            self.error_table.setAlternatingRowColors(True)
            
            # Header settings
            header = self.error_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.Stretch)
            
            # Populate table
            for row, error in enumerate(self.errors):
                # File path
                file_item = QTableWidgetItem(error['file'])
                self.error_table.setItem(row, 0, file_item)
                
                # Error type
                error_type = self.categorize_error(error['error'])
                type_item = QTableWidgetItem(error_type)
                self.error_table.setItem(row, 1, type_item)
                
                # Details
                details_item = QTableWidgetItem(error['error'])
                details_item.setToolTip(error['error'])
                self.error_table.setItem(row, 2, details_item)
            
            layout.addWidget(self.error_table)
            
            # Help text
            help_text = QTextEdit()
            help_text.setReadOnly(True)
            help_text.setMaximumHeight(120)
            help_text.setHtml("""
                <b>How to fix these errors:</b><br>
                <ul>
                <li><b>XML Parse Error:</b> File has invalid XML syntax. Open in text editor and fix mismatched tags.</li>
                <li><b>File Not Found:</b> Check file/folder name spelling and case in cfgeconomycore.xml.</li>
                <li><b>Invalid XML Declaration:</b> File may have comments before &lt;?xml&gt; tag. Move them after.</li>
                <li><b>Empty/Invalid Values:</b> File has empty or invalid numeric fields. App will use defaults.</li>
                </ul>
            """)
            layout.addWidget(help_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        if self.errors:
            copy_btn = QPushButton("Copy Error List")
            copy_btn.clicked.connect(self.copy_errors)
            button_layout.addWidget(copy_btn)
            
            retry_btn = QPushButton("Retry Failed Files")
            retry_btn.setStyleSheet("QPushButton { background-color: #0e639c; }")
            retry_btn.clicked.connect(self.retry_files)
            button_layout.addWidget(retry_btn)
        
        close_btn = QPushButton("Continue")
        close_btn.setDefault(True)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.retry_requested = False
    
    def retry_files(self):
        """Mark that user wants to retry failed files"""
        self.retry_requested = True
        self.accept()
    
    def categorize_error(self, error_msg: str) -> str:
        """Categorize error for display"""
        error_lower = error_msg.lower()
        
        if 'mismatched tag' in error_lower or 'parse' in error_lower:
            return "XML Parse Error"
        elif 'not found' in error_lower or 'path' in error_lower:
            return "File Not Found"
        elif 'xml declaration' in error_lower:
            return "Invalid XML Declaration"
        elif 'invalid literal' in error_lower or 'empty' in error_lower:
            return "Empty/Invalid Values"
        else:
            return "Unknown Error"
    
    def copy_errors(self):
        """Copy error list to clipboard"""
        error_text = f"File Loading Errors ({len(self.errors)} files)\n\n"
        
        for error in self.errors:
            error_text += f"File: {error['file']}\n"
            error_text += f"Error: {error['error']}\n\n"
        
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(error_text)
        
        # Show feedback
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Copied", "Error list copied to clipboard!")
