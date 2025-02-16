import json
import os
from datetime import datetime

class HistoryManager:
    def __init__(self):
        self.history_file = "pdf_history.json"
        self.history = self.load_history()
        
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
        
    def save_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
            
    def add_record(self, filepath, page=0):
        # 移除同文件的旧记录
        self.history = [h for h in self.history if h['filepath'] != filepath]
        
        # 添加新记录
        record = {
            'filepath': filepath,
            'filename': os.path.basename(filepath),
            'last_page': page,
            'last_read': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.history.insert(0, record)  # 添加到开头
        
        # 保持最多20条记录
        self.history = self.history[:20]
        self.save_history()
        
    def update_page(self, filepath, page):
        for record in self.history:
            if record['filepath'] == filepath:
                record['last_page'] = page
                record['last_read'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                break
        self.save_history() 