#!/usr/bin/env python3
"""
DayZ Types Editor - Main Entry Point
"""
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set dark theme
    app.setStyleSheet("""
        QMainWindow, QDialog, QWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        QTabWidget::pane {
            border: 1px solid #444;
            background-color: #1e1e1e;
        }
        QTabBar::tab {
            background-color: #2d2d2d;
            color: #999;
            padding: 10px 20px;
            border-right: 1px solid #444;
        }
        QTabBar::tab:selected {
            background-color: #1e1e1e;
            color: #4a9eff;
            border-bottom: 2px solid #4a9eff;
        }
        QPushButton {
            background-color: #0e639c;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #1177bb;
        }
        QPushButton:pressed {
            background-color: #0d5a8f;
        }
        QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #252526;
            border: 1px solid #444;
            color: #e0e0e0;
            padding: 6px;
            border-radius: 3px;
        }
        QTableWidget {
            background-color: #1e1e1e;
            gridline-color: #333;
            border: none;
        }
        QTableWidget::item {
            border-bottom: 1px solid #333;
            padding: 8px;
        }
        QTableWidget::item:selected {
            background-color: #264f78;
        }
        QHeaderView::section {
            background-color: #252526;
            color: #999;
            padding: 8px;
            border: none;
            border-bottom: 1px solid #444;
            font-weight: bold;
        }
        QScrollBar:vertical {
            background-color: #1e1e1e;
            width: 12px;
        }
        QScrollBar::handle:vertical {
            background-color: #555;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #666;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
