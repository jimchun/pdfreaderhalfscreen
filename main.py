import sys
import warnings
from PyQt6.QtWidgets import QApplication
from pdf_viewer import PDFViewer

# 过滤libpng警告
warnings.filterwarnings("ignore", category=UserWarning)

def main():
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 