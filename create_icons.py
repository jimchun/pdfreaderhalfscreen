from PIL import Image, ImageDraw
import os

def create_minimize_icon():
    img = Image.new('RGBA', (12, 12), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.line([(2, 6), (10, 6)], fill='black', width=1)
    img.save('icons/minimize.png')

def create_maximize_icon():
    img = Image.new('RGBA', (12, 12), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(2, 2), (10, 10)], outline='black', width=1)
    img.save('icons/maximize.png')

def create_restore_icon():
    img = Image.new('RGBA', (12, 12), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(4, 1), (11, 8)], outline='black', width=1)
    draw.rectangle([(1, 4), (8, 11)], outline='black', width=1)
    img.save('icons/restore.png')

def create_close_icon():
    img = Image.new('RGBA', (12, 12), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.line([(2, 2), (10, 10)], fill='black', width=1)
    draw.line([(2, 10), (10, 2)], fill='black', width=1)
    img.save('icons/close.png')

if __name__ == '__main__':
    if not os.path.exists('icons'):
        os.makedirs('icons')
    create_minimize_icon()
    create_maximize_icon()
    create_restore_icon()
    create_close_icon() 