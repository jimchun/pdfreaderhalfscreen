from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QListWidget, QListWidgetItem, QLabel, QFileDialog)
from PyQt6.QtCore import pyqtSignal
import os

class HistoryView(QWidget):
    fileSelected = pyqtSignal(str, int)  # 信号：发送文件路径和页码
    
    def __init__(self, history_manager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # 顶部按钮
        top_layout = QHBoxLayout()
        self.open_btn = QPushButton('打开PDF文件', self)
        self.open_btn.clicked.connect(self.openFile)
        top_layout.addWidget(self.open_btn)
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # 历史记录列表
        self.list_widget = QListWidget(self)
        self.list_widget.itemDoubleClicked.connect(self.onItemDoubleClicked)
        layout.addWidget(self.list_widget)
        
        self.updateList()
        
    def updateList(self):
        self.list_widget.clear()
        for record in self.history_manager.history:
            item = QListWidgetItem()
            widget = QWidget()
            layout = QHBoxLayout(widget)
            
            # 文件名和最后阅读时间
            info_layout = QVBoxLayout()
            filename_label = QLabel(record['filename'])
            time_label = QLabel(f"上次阅读: {record['last_read']}")
            time_label.setStyleSheet("color: gray; font-size: 10px;")
            info_layout.addWidget(filename_label)
            info_layout.addWidget(time_label)
            
            layout.addLayout(info_layout)
            layout.addStretch()
            
            # 页码信息
            page_label = QLabel(f"第 {record['last_page'] + 1} 页")
            layout.addWidget(page_label)
            
            widget.setLayout(layout)
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            
    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "选择PDF文件",
            os.path.expanduser("~"),
            "PDF files (*.pdf)"
        )
        if filename:
            self.fileSelected.emit(filename, 0)
            
    def onItemDoubleClicked(self, item):
        index = self.list_widget.row(item)
        record = self.history_manager.history[index]
        if os.path.exists(record['filepath']):
            self.fileSelected.emit(record['filepath'], record['last_page']) 