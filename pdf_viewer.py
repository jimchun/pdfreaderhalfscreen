from PyQt6.QtWidgets import (QMainWindow, QGraphicsView, QGraphicsScene,
                          QFileDialog, QGraphicsPixmapItem, QMenuBar,
                          QWidget, QHBoxLayout, QToolButton, QApplication)
from PyQt6.QtCore import Qt, QRectF, QTimer, QPoint, QSize
from PyQt6.QtGui import (QKeySequence, QShortcut, QImage, QPixmap, QAction, 
                       QCursor, QIcon, QPainter)
import fitz
import os
from history_manager import HistoryManager
from history_view import HistoryView

class TitleBarButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(45, 25)  # Windows默认尺寸
        self.setIconSize(QSize(12, 12))
        self.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
            }
            QToolButton:hover {
                background-color: #e5e5e5;
            }
            QToolButton:pressed {
                background-color: #ccc;
            }
        """)

class WindowControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # 最小化按钮
        self.minimize_button = TitleBarButton(self)
        self.minimize_button.setIcon(QIcon("icons/minimize.png"))  # 需要添加图标文件
        self.minimize_button.clicked.connect(self.parent().showMinimized)

        # 最大化/还原按钮
        self.maximize_button = TitleBarButton(self)
        self.maximize_button.setIcon(QIcon("icons/maximize.png"))
        self.maximize_button.clicked.connect(self.toggleMaximize)

        # 关闭按钮
        self.close_button = TitleBarButton(self)
        self.close_button.setIcon(QIcon("icons/close.png"))
        self.close_button.setStyleSheet("""
            QToolButton:hover {
                background-color: #e81123;
                color: white;
            }
            QToolButton:pressed {
                background-color: #f1707a;
            }
        """)
        self.close_button.clicked.connect(self.parent().close)

        # 添加按钮到布局
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)

    def toggleMaximize(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(QIcon("icons/maximize.png"))
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(QIcon("icons/restore.png"))

class PDFGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        # 启用抗锯齿
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        # 优化视图质量
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
    def mouseMoveEvent(self, event):
        if self.parent():
            self.parent().handleMouseMove()
        super().mouseMoveEvent(event)

class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_page = 0
        self.doc = None
        self.current_file = None
        self.history_manager = HistoryManager()
        self.menu_height = 25
        self.menu_show_area = 50
        self.menu_timer = QTimer()
        self.menu_timer.timeout.connect(self.hideMenuBar)
        self.menu_timer.setSingleShot(True)
        # 获取屏幕DPI
        self.screen_dpi = QApplication.primaryScreen().logicalDotsPerInch()
        self.zoom_factor = self.screen_dpi / 72.0  # 72是PDF的基准DPI
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('PDFreadbot')
        
        # 隐藏默认标题栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # 获取屏幕实际分辨率
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        
        # 设置窗口大小：宽度为屏幕宽度的一半，高度保持屏幕完整高度
        window_width = screen_geometry.width() // 2
        window_height = screen_geometry.height()
        self.resize(window_width, window_height)
        
        # 将窗口移动到屏幕左侧
        self.move(0, 0)
        
        # 创建视图和场景，使用自定义的PDFGraphicsView
        self.view = PDFGraphicsView(self)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        
        # 创建历史记录视图
        self.history_view = HistoryView(self.history_manager, self)
        self.history_view.fileSelected.connect(self.loadPDF)
        self.setCentralWidget(self.history_view)
        
        # 创建菜单栏
        self.createMenus()
        
        # 初始隐藏菜单栏
        self.menuBar().hide()
        
        # 设置快捷键
        self.setupShortcuts()
        
        # 启用鼠标追踪
        self.setMouseTracking(True)
        
        # 创建并添加窗口控制按钮
        self.window_controls = WindowControls(self)
        self.window_controls.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 6px;
            }
            QToolButton:hover {
                background-color: #3a3a3a;
            }
            QToolButton:pressed {
                background-color: #404040;
            }
            #closeButton:hover {
                background-color: #e81123;
            }
            #closeButton:pressed {
                background-color: #f1707a;
            }
        """)
        self.menuBar().setCornerWidget(self.window_controls, Qt.Corner.TopRightCorner)
        
        # 设置菜单栏样式
        self.menuBar().setStyleSheet("""
            QMenuBar {
                background-color: #2b2b2b;
                color: #ffffff;
                padding: 2px;
                font-size: 14px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 10px;
                margin: 0px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #3a3a3a;
            }
            QMenuBar::item:pressed {
                background-color: #404040;
            }
            QMenu {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #404040;
                padding: 5px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 2px;
            }
            QMenu::item:selected {
                background-color: #3a3a3a;
            }
            QMenu::separator {
                height: 1px;
                background-color: #404040;
                margin: 5px 0px;
            }
        """)

    def createMenus(self):
        # 文件菜单
        fileMenu = self.menuBar().addMenu('文件')
        fileMenu.setStyleSheet("""
            QMenu {
                font-size: 13px;
            }
        """)
        
        openAction = QAction('打开', self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.openFile)
        fileMenu.addAction(openAction)
        
        exitAction = QAction('退出', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)
        
        # 导航菜单
        navMenu = self.menuBar().addMenu('导航')
        
        nextAction = QAction('下一页', self)
        nextAction.setShortcut('Right')
        nextAction.triggered.connect(self.nextPage)
        navMenu.addAction(nextAction)
        
        prevAction = QAction('上一页', self)
        prevAction.setShortcut('Left')
        prevAction.triggered.connect(self.prevPage)
        navMenu.addAction(prevAction)
        
    def handleMouseMove(self):
        # 获取鼠标在窗口中的位置
        window_pos = self.mapFromGlobal(QCursor.pos())
        
        if window_pos.y() <= self.menu_show_area:
            self.showMenuBar()
        else:
            # 启动定时器，准备隐藏菜单
            if not self.menu_timer.isActive():
                self.menu_timer.start(2000)
    
    def mousePressEvent(self, event):
        # 记录鼠标按下时的位置，用于窗口拖动
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() <= self.menu_height:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        
    def mouseMoveEvent(self, event):
        # 处理窗口拖动
        if event.buttons() & Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
            if event.position().y() <= self.menu_height:
                self.move(event.globalPosition().toPoint() - self.drag_position)
        
        # 处理菜单显示/隐藏
        self.handleMouseMove()
        super().mouseMoveEvent(event)
        
    def showMenuBar(self):
        if not self.menuBar().isVisible():
            self.menuBar().show()
        # 停止之前的定时器
        self.menu_timer.stop()
        
    def hideMenuBar(self):
        # 获取当前鼠标位置
        window_pos = self.mapFromGlobal(QCursor.pos())
        # 只有当鼠标不在菜单区域时才隐藏
        if window_pos.y() > self.menu_show_area:
            self.menuBar().hide()

    def setupShortcuts(self):
        # Esc退出全屏
        self.shortcut_exit = QShortcut(QKeySequence('Esc'), self)
        self.shortcut_exit.activated.connect(self.close)
        
        # 翻页快捷键
        self.shortcut_next = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        self.shortcut_next.activated.connect(self.nextPage)
        
        self.shortcut_prev = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        self.shortcut_prev.activated.connect(self.prevPage)
        
    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "选择PDF文件",
            os.path.expanduser("~"),
            "PDF files (*.pdf)"
        )
        if filename:
            self.loadPDF(filename)
            
    def loadPDF(self, filename, page=0):
        try:
            self.current_file = filename
            self.doc = fitz.open(filename)
            # 切换中心部件为PDF视图
            self.setCentralWidget(self.view)
            self.showPage(page)
            # 添加到历史记录
            self.history_manager.add_record(filename, page)
        except Exception as e:
            print(f"Error loading PDF: {e}")
            
    def showPage(self, page_num):
        if not self.doc or page_num < 0 or page_num >= len(self.doc):
            return
            
        self.current_page = page_num
        page = self.doc[page_num]
        
        # 计算缩放矩阵
        zoom_matrix = fitz.Matrix(self.zoom_factor, self.zoom_factor)
        
        # 使用高质量渲染设置
        pix = page.get_pixmap(
            matrix=zoom_matrix,
            alpha=False,  # 不需要透明通道
            colorspace="rgb",  # 使用RGB颜色空间
        )
        
        # 将Pixmap转换为QImage，使用优化的格式
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
        
        # 清除场景并显示新页面
        self.scene.clear()
        pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(img))
        self.scene.addItem(pixmap_item)
        
        # 设置场景大小
        self.scene.setSceneRect(pixmap_item.boundingRect())
        
        # 调整视图大小以适应页面
        self.view.fitInView(pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        
        # 更新历史记录中的页码
        if self.current_file:
            self.history_manager.update_page(self.current_file, page_num)
        
    def nextPage(self):
        if self.doc and self.current_page < len(self.doc) - 1:
            self.showPage(self.current_page + 1)
            
    def prevPage(self):
        if self.doc and self.current_page > 0:
            self.showPage(self.current_page - 1)
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 重新调整页面大小，保持清晰度
        if self.scene.items():
            # 获取当前页面重新渲染
            if hasattr(self, 'current_page') and self.doc:
                self.showPage(self.current_page) 