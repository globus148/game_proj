# from PIL import Image, ImageDraw
#
# # Размеры спрайта
# BLOCK_SIZE = 30
# SPRITES_COUNT = 7
# CANVAS_WIDTH = BLOCK_SIZE * SPRITES_COUNT
# CANVAS_HEIGHT = BLOCK_SIZE
#
# # Цвета для фигур (RGBA)
# COLORS = {
#     'I': (0, 255, 255, 255),  # Голубой
#     'O': (255, 255, 0, 255),  # Желтый
#     'T': (128, 0, 128, 255),  # Фиолетовый
#     'L': (255, 165, 0, 255),  # Оранжевый
#     'J': (0, 0, 255, 255),  # Синий
#     'S': (0, 255, 0, 255),  # Зеленый
#     'Z': (255, 0, 0, 255)  # Красный
# }
#
# # Создаем новое изображение
# img = Image.new('RGBA', (CANVAS_WIDTH, CANVAS_HEIGHT), (0, 0, 0, 0))
# draw = ImageDraw.Draw(img)
#
# # Рисуем спрайты для каждой фигуры
# for i, (shape, color) in enumerate(COLORS.items()):
#     # Координаты левого верхнего угла
#     x0 = i * BLOCK_SIZE
#     y0 = 0
#
#     # Рисуем базовый блок
#     draw.rectangle([x0, y0, x0 + BLOCK_SIZE - 1, y0 + BLOCK_SIZE - 1], fill=color)
#
#     # Добавляем 3D-эффект
#     draw.rectangle([x0, y0, x0 + BLOCK_SIZE - 1, y0 + 2], fill=(255, 255, 255, 100))  # Верхняя подсветка
#     draw.rectangle([x0, y0 + BLOCK_SIZE - 3, x0 + BLOCK_SIZE - 1, y0 + BLOCK_SIZE - 1],
#                    fill=(0, 0, 0, 100))  # Нижняя тень
#     draw.rectangle([x0, y0, x0 + 2, y0 + BLOCK_SIZE - 1], fill=(255, 255, 255, 100))  # Левая подсветка
#     draw.rectangle([x0 + BLOCK_SIZE - 3, y0, x0 + BLOCK_SIZE - 1, y0 + BLOCK_SIZE - 1],
#                    fill=(0, 0, 0, 100))  # Правая тень
#
# # Сохраняем изображение
# img.save('tetris_sprites.png', 'PNG')




from PIL import Image, ImageDraw

# Размер блока
BLOCK_SIZE = 30
SPRITES_COUNT = 7
CANVAS_WIDTH = BLOCK_SIZE * SPRITES_COUNT
CANVAS_HEIGHT = BLOCK_SIZE

# Цвета фигур (RGBA)
COLORS = {
    'I': (0, 255, 255, 255),  # Голубой
    'O': (255, 255, 0, 255),  # Желтый
    'T': (128, 0, 128, 255),  # Фиолетовый
    'L': (255, 165, 0, 255),  # Оранжевый
    'J': (0, 0, 255, 255),  # Синий
    'S': (0, 255, 0, 255),  # Зеленый
    'Z': (255, 0, 0, 255)  # Красный
}

# Создаем изображение
img = Image.new('RGBA', (CANVAS_WIDTH, CANVAS_HEIGHT), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Функция для отрисовки одного блока с 3D-эффектом
def draw_block(draw, x0, y0, color):
    base_color = color
    light_color = tuple(min(255, c + 80) for c in color[:3]) + (255,)  # Осветление
    dark_color = tuple(max(0, c - 80) for c in color[:3]) + (255,)  # Затемнение
    shadow_color = tuple(max(0, c - 120) for c in color[:3]) + (180,)  # Глубокая тень

    # Основной блок
    draw.rectangle([x0, y0, x0 + BLOCK_SIZE - 1, y0 + BLOCK_SIZE - 1], fill=base_color)

    # Верхняя подсветка
    draw.polygon(
        [(x0, y0), (x0 + BLOCK_SIZE, y0), (x0 + BLOCK_SIZE - 5, y0 + 5), (x0 + 5, y0 + 5)],
        fill=light_color
    )

    # Левая подсветка
    draw.polygon(
        [(x0, y0), (x0, y0 + BLOCK_SIZE), (x0 + 5, y0 + BLOCK_SIZE - 5), (x0 + 5, y0 + 5)],
        fill=light_color
    )

    # Правая тень
    draw.polygon(
        [(x0 + BLOCK_SIZE, y0), (x0 + BLOCK_SIZE, y0 + BLOCK_SIZE), (x0 + BLOCK_SIZE - 5, y0 + BLOCK_SIZE - 5), (x0 + BLOCK_SIZE - 5, y0 + 5)],
        fill=dark_color
    )

    # Нижняя тень
    draw.polygon(
        [(x0, y0 + BLOCK_SIZE), (x0 + BLOCK_SIZE, y0 + BLOCK_SIZE), (x0 + BLOCK_SIZE - 5, y0 + BLOCK_SIZE - 5), (x0 + 5, y0 + BLOCK_SIZE - 5)],
        fill=shadow_color
    )

# Отрисовка всех фигур
for i, (shape, color) in enumerate(COLORS.items()):
    x0 = i * BLOCK_SIZE
    y0 = 0
    draw_block(draw, x0, y0, color)

# Сохраняем изображение
img.save('tetris_sprites.png', 'PNG')


