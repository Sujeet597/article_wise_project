"""
MSA Stock Analysis - Desktop Application
PyQt5-based GUI for folder browsing and file management
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
from typing import List, Dict

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QFileDialog, QTableWidget,
    QTableWidgetItem, QTabWidget, QComboBox, QSpinBox, QMessageBox,
    QProgressBar, QStatusBar, QSplitter, QTreeWidget, QTreeWidgetItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QColor, QFont
from PyQt5.QtCore import QTimer

from msa_stock_analysis import MSAStockAnalysis


class FileListWorker(QThread):
    """Worker thread to load files without blocking UI"""
    files_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    progress_update = pyqtSignal(str)
    
    def __init__(self, folder_path: str):
        super().__init__()
        self.folder_path = folder_path
    
    def run(self):
        try:
            self.progress_update.emit(f"Scanning folder: {self.folder_path}")
            files = self._scan_folder(self.folder_path)
            self.files_loaded.emit(files)
        except Exception as e:
            self.error_occurred.emit(f"Error scanning folder: {str(e)}")
    
    def _scan_folder(self, folder_path: str) -> List[Dict]:
        """Recursively scan folder and return file list"""
        files = []
        try:
            for root, dirs, filenames in os.walk(folder_path):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    rel_path = os.path.relpath(filepath, folder_path)
                    
                    try:
                        file_size = os.path.getsize(filepath)
                        mod_time = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M')
                        ext = os.path.splitext(filename)[1].lower()
                        
                        files.append({
                            'name': filename,
                            'path': filepath,
                            'rel_path': rel_path,
                            'size': self._format_size(file_size),
                            'size_bytes': file_size,
                            'modified': mod_time,
                            'type': ext if ext else 'unknown'
                        })
                    except Exception as e:
                        print(f"Error processing file {filepath}: {e}")
                        continue
        except Exception as e:
            print(f"Error scanning folder: {e}")
        
        return files
    
    @staticmethod
    def _format_size(size_bytes):
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"


class MSAWorker(QThread):
    """Worker thread to run MSA pipeline without blocking UI"""
    pipeline_started = pyqtSignal()
    pipeline_progress = pyqtSignal(str)
    pipeline_completed = pyqtSignal(bool, str)
    
    def __init__(self, msa_csv_path, store_master_path, base_data_folder, 
                 list_data_folder, mrst_path, output_folder):
        super().__init__()
        self.msa_csv_path = msa_csv_path
        self.store_master_path = store_master_path
        self.base_data_folder = base_data_folder
        self.list_data_folder = list_data_folder
        self.mrst_path = mrst_path
        self.output_folder = output_folder
    
    def run(self):
        try:
            self.pipeline_started.emit()
            
            pipeline = MSAStockAnalysis(
                msa_csv_path=self.msa_csv_path,
                store_master_path=self.store_master_path,
                base_data_folder=self.base_data_folder,
                list_data_folder=self.list_data_folder,
                mrst_path=self.mrst_path,
                output_folder=self.output_folder
            )
            
            self.pipeline_progress.emit("Starting pipeline...")
            
            success = pipeline.run_pipeline()
            
            if success:
                self.pipeline_completed.emit(True, "Pipeline completed successfully!")
            else:
                self.pipeline_completed.emit(False, "Pipeline completed with errors")
                
        except Exception as e:
            self.pipeline_completed.emit(False, f"Error: {str(e)}")


class MSADesktopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MSA Stock Analysis - Desktop App")
        self.setGeometry(100, 100, 1200, 800)
        
        # Data storage
        self.current_folder = None
        self.files_list = []
        self.file_worker = None
        self.msa_worker = None
        
        # Setup UI
        self.init_ui()
        self.apply_styles()
        
    def init_ui(self):
        """Initialize User Interface"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout(main_widget)
        
        # ==================== TAB 1: FILE BROWSER ====================
        
        # Create tabs
        tabs = QTabWidget()
        
        # Tab 1: File Browser
        file_browser_widget = QWidget()
        file_browser_layout = QVBoxLayout(file_browser_widget)
        
        # Folder selection section
        folder_section = QHBoxLayout()
        
        folder_label = QLabel("📁 Select Folder:")
        folder_label.setFont(QFont("Arial", 10, QFont.Bold))
        folder_section.addWidget(folder_label)
        
        self.folder_path_input = QLineEdit()
        self.folder_path_input.setPlaceholderText("Enter or browse folder path...")
        self.folder_path_input.setReadOnly(True)
        folder_section.addWidget(self.folder_path_input)
        
        browse_btn = QPushButton("🔍 Browse")
        browse_btn.clicked.connect(self.browse_folder)
        browse_btn.setFixedWidth(120)
        folder_section.addWidget(browse_btn)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_files)
        refresh_btn.setFixedWidth(120)
        folder_section.addWidget(refresh_btn)
        
        file_browser_layout.addLayout(folder_section)
        
        # Filter section
        filter_section = QHBoxLayout()
        filter_section.addWidget(QLabel("Filter by Type:"))
        
        self.file_type_filter = QComboBox()
        self.file_type_filter.addItems(["All Files", ".csv", ".xlsx", ".xls", ".json", ".txt"])
        self.file_type_filter.currentTextChanged.connect(self.apply_filter)
        filter_section.addWidget(self.file_type_filter)
        
        filter_section.addStretch()
        self.file_count_label = QLabel("Files: 0")
        self.file_count_label.setFont(QFont("Arial", 9, QFont.Bold))
        filter_section.addWidget(self.file_count_label)
        
        file_browser_layout.addLayout(filter_section)
        
        # File table
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(5)
        self.file_table.setHorizontalHeaderLabels(["File Name", "Type", "Size", "Modified", "Path"])
        self.file_table.horizontalHeader().setStretchLastSection(True)
        self.file_table.setColumnWidth(0, 250)
        self.file_table.setColumnWidth(1, 80)
        self.file_table.setColumnWidth(2, 100)
        self.file_table.setColumnWidth(3, 150)
        self.file_table.setSelectionBehavior(self.file_table.SelectRows)
        
        file_browser_layout.addWidget(QLabel("📋 Files in Folder:"))
        file_browser_layout.addWidget(self.file_table)
        
        # File details section
        details_section = QHBoxLayout()
        details_section.addWidget(QLabel("Selected File:"))
        self.selected_file_label = QLabel("None")
        self.selected_file_label.setStyleSheet("color: blue; font-weight: bold;")
        details_section.addWidget(self.selected_file_label)
        details_section.addStretch()
        
        file_browser_layout.addLayout(details_section)
        
        tabs.addTab(file_browser_widget, "📂 File Browser")
        
        # ==================== TAB 2: MSA PIPELINE ====================
        
        pipeline_widget = QWidget()
        pipeline_layout = QVBoxLayout(pipeline_widget)
        
        # Pipeline config section
        config_label = QLabel("🔧 Configure MSA Pipeline")
        config_label.setFont(QFont("Arial", 11, QFont.Bold))
        pipeline_layout.addWidget(config_label)
        
        # File inputs
        files_config = QVBoxLayout()
        
        # MSA CSV
        msa_layout = QHBoxLayout()
        msa_layout.addWidget(QLabel("MSA CSV File:"))
        self.msa_csv_input = QLineEdit()
        self.msa_csv_input.setPlaceholderText("Select MSA CSV file...")
        msa_layout.addWidget(self.msa_csv_input)
        msa_browse = QPushButton("Browse")
        msa_browse.setFixedWidth(100)
        msa_browse.clicked.connect(lambda: self.select_file_dialog("Select MSA CSV", self.msa_csv_input, "*.csv"))
        msa_layout.addWidget(msa_browse)
        files_config.addLayout(msa_layout)
        
        # Store Master
        store_layout = QHBoxLayout()
        store_layout.addWidget(QLabel("Store Master File:"))
        self.store_master_input = QLineEdit()
        self.store_master_input.setPlaceholderText("Select Store Master Excel file...")
        store_layout.addWidget(self.store_master_input)
        store_browse = QPushButton("Browse")
        store_browse.setFixedWidth(100)
        store_browse.clicked.connect(lambda: self.select_file_dialog("Select Store Master", self.store_master_input, "*.xlsx *.xls"))
        store_layout.addWidget(store_browse)
        files_config.addLayout(store_layout)
        
        # Base Data Folder
        base_layout = QHBoxLayout()
        base_layout.addWidget(QLabel("BASE DATA Folder:"))
        self.base_data_input = QLineEdit()
        self.base_data_input.setPlaceholderText("Select BASE DATA folder...")
        base_layout.addWidget(self.base_data_input)
        base_browse = QPushButton("Browse")
        base_browse.setFixedWidth(100)
        base_browse.clicked.connect(lambda: self.select_folder_dialog("Select BASE DATA Folder", self.base_data_input))
        base_layout.addWidget(base_browse)
        files_config.addLayout(base_layout)
        
        # List Data Folder
        list_layout = QHBoxLayout()
        list_layout.addWidget(QLabel("LIST DATA Folder:"))
        self.list_data_input = QLineEdit()
        self.list_data_input.setPlaceholderText("Select LIST DATA folder...")
        list_layout.addWidget(self.list_data_input)
        list_browse = QPushButton("Browse")
        list_browse.setFixedWidth(100)
        list_browse.clicked.connect(lambda: self.select_folder_dialog("Select LIST DATA Folder", self.list_data_input))
        list_layout.addWidget(list_browse)
        files_config.addLayout(list_layout)
        
        # MRST File
        mrst_layout = QHBoxLayout()
        mrst_layout.addWidget(QLabel("MRST File:"))
        self.mrst_input = QLineEdit()
        self.mrst_input.setPlaceholderText("Select MRST Excel file...")
        mrst_layout.addWidget(self.mrst_input)
        mrst_browse = QPushButton("Browse")
        mrst_browse.setFixedWidth(100)
        mrst_browse.clicked.connect(lambda: self.select_file_dialog("Select MRST File", self.mrst_input, "*.xlsx *.xls"))
        mrst_layout.addWidget(mrst_browse)
        files_config.addLayout(mrst_layout)
        
        pipeline_layout.addLayout(files_config)
        
        # Output folder
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Folder:"))
        self.output_input = QLineEdit()
        self.output_input.setText("output")
        output_layout.addWidget(self.output_input)
        output_browse = QPushButton("Browse")
        output_browse.setFixedWidth(100)
        output_browse.clicked.connect(lambda: self.select_folder_dialog("Select Output Folder", self.output_input))
        output_layout.addWidget(output_browse)
        pipeline_layout.addLayout(output_layout)
        
        pipeline_layout.addSpacing(20)
        
        # Run button
        run_btn = QPushButton("▶️ Run MSA Pipeline")
        run_btn.setFixedHeight(50)
        run_btn.setFont(QFont("Arial", 11, QFont.Bold))
        run_btn.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px;")
        run_btn.clicked.connect(self.run_pipeline)
        pipeline_layout.addWidget(run_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        pipeline_layout.addWidget(self.progress_bar)
        
        # Status text
        self.status_text = QLabel("")
        self.status_text.setStyleSheet("color: green; font-weight: bold;")
        pipeline_layout.addWidget(self.status_text)
        
        pipeline_layout.addStretch()
        
        tabs.addTab(pipeline_widget, "⚙️ MSA Pipeline")
        
        # ==================== TAB 3: FILE TREE ====================
        
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        
        tree_label = QLabel("🌳 Folder Structure")
        tree_label.setFont(QFont("Arial", 10, QFont.Bold))
        tree_layout.addWidget(tree_label)
        
        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabels(["Name", "Type", "Size"])
        self.folder_tree.setColumnWidth(0, 300)
        
        tree_layout.addWidget(self.folder_tree)
        
        tabs.addTab(tree_widget, "🌳 Folder Structure")
        
        main_layout.addWidget(tabs)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def apply_styles(self):
        """Apply custom styles"""
        stylesheet = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QLabel {
            color: #333;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #0b7dda;
        }
        QPushButton:pressed {
            background-color: #0056b3;
        }
        QLineEdit {
            border: 1px solid #ddd;
            padding: 8px;
            border-radius: 4px;
            background-color: white;
        }
        QTableWidget {
            border: 1px solid #ddd;
            gridline-color: #eee;
        }
        QHeaderView::section {
            background-color: #2196F3;
            color: white;
            padding: 5px;
            border: none;
        }
        QComboBox {
            border: 1px solid #ddd;
            padding: 5px;
            border-radius: 4px;
        }
        """
        self.setStyleSheet(stylesheet)
    
    def browse_folder(self):
        """Browse and select a folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            os.path.expanduser("~")
        )
        
        if folder:
            self.folder_path_input.setText(folder)
            self.current_folder = folder
            self.load_files()
    
    def load_files(self):
        """Load files from selected folder"""
        if not self.current_folder:
            return
        
        self.statusBar().showMessage("Loading files...")
        self.file_worker = FileListWorker(self.current_folder)
        self.file_worker.files_loaded.connect(self.on_files_loaded)
        self.file_worker.error_occurred.connect(self.on_error)
        self.file_worker.progress_update.connect(self.on_progress)
        self.file_worker.start()
    
    def on_files_loaded(self, files):
        """Handle files loaded"""
        self.files_list = files
        self.display_files(self.files_list)
        self.build_folder_tree()
        self.statusBar().showMessage(f"Loaded {len(files)} files")
    
    def on_error(self, error_msg):
        """Handle errors"""
        QMessageBox.critical(self, "Error", error_msg)
        self.statusBar().showMessage("Error loading files")
    
    def on_progress(self, message):
        """Handle progress updates"""
        self.statusBar().showMessage(message)
    
    def display_files(self, files):
        """Display files in table"""
        self.file_table.setRowCount(0)
        
        for file_info in files:
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)
            
            self.file_table.setItem(row, 0, QTableWidgetItem(file_info['name']))
            self.file_table.setItem(row, 1, QTableWidgetItem(file_info['type']))
            self.file_table.setItem(row, 2, QTableWidgetItem(file_info['size']))
            self.file_table.setItem(row, 3, QTableWidgetItem(file_info['modified']))
            self.file_table.setItem(row, 4, QTableWidgetItem(file_info['path']))
            
            # Color code by type
            if file_info['type'] in ['.csv', '.xlsx', '.xls']:
                for col in range(5):
                    self.file_table.item(row, col).setBackground(QColor(200, 230, 201))
        
        self.file_count_label.setText(f"Files: {len(files)}")
        
        # Connect table selection
        self.file_table.itemSelectionChanged.connect(self.on_file_selected)
    
    def on_file_selected(self):
        """Handle file selection in table"""
        selected_rows = self.file_table.selectedIndexes()
        if selected_rows:
            row = selected_rows[0].row()
            file_path = self.file_table.item(row, 4).text()
            file_name = self.file_table.item(row, 0).text()
            self.selected_file_label.setText(f"{file_name} ({file_path})")
    
    def apply_filter(self):
        """Apply file type filter"""
        filter_type = self.file_type_filter.currentText()
        
        if filter_type == "All Files":
            self.display_files(self.files_list)
        else:
            filtered = [f for f in self.files_list if f['type'] == filter_type]
            self.display_files(filtered)
    
    def refresh_files(self):
        """Refresh file list"""
        if self.current_folder:
            self.load_files()
    
    def build_folder_tree(self):
        """Build folder structure tree"""
        self.folder_tree.clear()
        
        if not self.current_folder:
            return
        
        root_item = QTreeWidgetItem([os.path.basename(self.current_folder), "Folder", ""])
        self.folder_tree.addTopLevelItem(root_item)
        
        self._add_tree_items(root_item, self.current_folder)
    
    def _add_tree_items(self, parent_item, folder_path):
        """Recursively add items to tree"""
        try:
            items = []
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isdir(item_path):
                    items.append((item, item_path, True))
                else:
                    size = os.path.getsize(item_path)
                    size_str = FileListWorker._format_size(size)
                    items.append((item, item_path, False, size_str))
            
            for item_data in sorted(items):
                if item_data[2]:  # Is directory
                    folder_item = QTreeWidgetItem([item_data[0], "Folder", ""])
                    parent_item.addChild(folder_item)
                    self._add_tree_items(folder_item, item_data[1])
                else:  # Is file
                    file_item = QTreeWidgetItem([item_data[0], "File", item_data[3]])
                    parent_item.addChild(file_item)
        except Exception as e:
            print(f"Error building tree: {e}")
    
    def select_file_dialog(self, title, line_edit, file_filter):
        """Open file selection dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            title,
            os.path.expanduser("~"),
            f"Files ({file_filter})"
        )
        if file_path:
            line_edit.setText(file_path)
    
    def select_folder_dialog(self, title, line_edit):
        """Open folder selection dialog"""
        folder_path = QFileDialog.getExistingDirectory(self, title, os.path.expanduser("~"))
        if folder_path:
            line_edit.setText(folder_path)
    
    def run_pipeline(self):
        """Run MSA pipeline"""
        # Validate inputs
        if not self.msa_csv_input.text():
            QMessageBox.warning(self, "Warning", "Please select MSA CSV file")
            return
        if not self.store_master_input.text():
            QMessageBox.warning(self, "Warning", "Please select Store Master file")
            return
        if not self.base_data_input.text():
            QMessageBox.warning(self, "Warning", "Please select BASE DATA folder")
            return
        if not self.list_data_input.text():
            QMessageBox.warning(self, "Warning", "Please select LIST DATA folder")
            return
        if not self.mrst_input.text():
            QMessageBox.warning(self, "Warning", "Please select MRST file")
            return
        
        # Disable button and show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_text.setText("Running pipeline...")
        
        # Run in separate thread
        self.msa_worker = MSAWorker(
            self.msa_csv_input.text(),
            self.store_master_input.text(),
            self.base_data_input.text(),
            self.list_data_input.text(),
            self.mrst_input.text(),
            self.output_input.text()
        )
        self.msa_worker.pipeline_completed.connect(self.on_pipeline_completed)
        self.msa_worker.start()
    
    def on_pipeline_completed(self, success, message):
        """Handle pipeline completion"""
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_text.setText(f"✅ {message}")
            self.status_text.setStyleSheet("color: green; font-weight: bold;")
            QMessageBox.information(self, "Success", message)
        else:
            self.status_text.setText(f"❌ {message}")
            self.status_text.setStyleSheet("color: red; font-weight: bold;")
            QMessageBox.warning(self, "Error", message)
        
        self.statusBar().showMessage("Ready")


def main():
    app = QApplication(sys.argv)
    window = MSADesktopApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
