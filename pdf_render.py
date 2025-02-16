import fitz

class PDFRenderer:
    def __init__(self):
        self.doc = None
        
    def load_document(self, path):
        try:
            self.doc = fitz.open(path)
            return True
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return False
            
    def render_page(self, page_num):
        if not self.doc:
            return None
        try:
            page = self.doc[page_num]
            pix = page.get_pixmap()
            return pix
        except Exception as e:
            print(f"Error rendering page: {e}")
            return None 