import os
import shutil
import subprocess

# 确保dist目录存在且为空
if os.path.exists('dist'):
    shutil.rmtree('dist')
os.makedirs('dist')

# 确保icons目录存在
if not os.path.exists('icons'):
    os.makedirs('icons')

# 确保有历史记录文件
if not os.path.exists('pdf_history.json'):
    with open('pdf_history.json', 'w', encoding='utf-8') as f:
        f.write('[]')

# 首先生成spec文件
subprocess.run(['pyi-makespec',
               '--name=PDFreadbot',
               '--windowed',
               '--onefile',
               '--add-data=icons;icons',
               '--add-data=pdf_history.json;.',
               'main.py'])

# 使用生成的spec文件打包
subprocess.run(['pyinstaller', 'PDFreadbot.spec', '--clean'])

print("打包完成！") 