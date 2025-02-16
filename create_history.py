import json

# 创建空的历史记录文件
with open('pdf_history.json', 'w', encoding='utf-8') as f:
    json.dump([], f) 