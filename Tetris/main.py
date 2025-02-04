import pygame
import sys
import random
import sqlite3


class Colors:
    purple = (160, 0, 249)
    cyan = (21, 204, 200)
    blue = (13, 64, 216)
    white = (255, 255, 255)
    dark_blue = (44, 44, 127)
    light_blue = (59, 85, 162)
    dark_grey = (26, 31, 40)
    green = (47, 231, 24)
    red = (231, 19, 18)
    orange = (228, 117, 18)
    yellow = (230, 235, 5)

    @classmethod
    def get_cell_colors(cls):
        return [cls.dark_grey, cls.green, cls.red, cls.orange, cls.yellow, cls.purple, cls.cyan, cls.blue]


class Position:
    def __init__(self, row, column):
        self.row = row
        self.column = column


class Block:
    def __init__(self, id):
        self.id = id
        self.cells = {}
        self.cell_size = 30
        self.row_offset = 0
        self.column_offset = 0
        self.rotation_state = 0
        self.colors = Colors.get_cell_colors()

    def move(self, rows, columns):
        self.row_offset += rows
        self.column_offset += columns

    def get_cell_positions(self):
        tiles = self.cells[self.rotation_state]
        moved_tiles = []
        for position in tiles:
            position = Position(position.row + self.row_offset, position.column + self.column_offset)
            moved_tiles.append(position)
        return moved_tiles

    def rotate(self):
        self.rotation_state += 1
        if self.rotation_state == len(self.cells):
            self.rotation_state = 0

    def undo_rotation(self):
        self.rotation_state -= 1
        if self.rotation_state == -1:
            self.rotation_state = len(self.cells) - 1

    def draw(self, screen, offset_x, offset_y):
        tiles = self.get_cell_positions()
        for tile in tiles:
            x = offset_x + tile.column * self.cell_size
            y = offset_y + tile.row * self.cell_size
            screen.blit(SPRITES[self.id], (x, y))


class LBlock(Block):
    def __init__(self):
        super().__init__(id=1)
        self.cells = {
            0: [Position(0, 2), Position(1, 0), Position(1, 1), Position(1, 2)],
            1: [Position(0, 1), Position(1, 1), Position(2, 1), Position(2, 2)],
            2: [Position(1, 0), Position(1, 1), Position(1, 2), Position(2, 0)],
            3: [Position(0, 0), Position(0, 1), Position(1, 1), Position(2, 1)]
        }
        self.move(0, 3)


class JBlock(Block):
    def __init__(self):
        super().__init__(id=2)
        self.cells = {
            0: [Position(0, 0), Position(1, 0), Position(1, 1), Position(1, 2)],
            1: [Position(0, 1), Position(0, 2), Position(1, 1), Position(2, 1)],
            2: [Position(1, 0), Position(1, 1), Position(1, 2), Position(2, 2)],
            3: [Position(0, 1), Position(1, 1), Position(2, 0), Position(2, 1)]
        }
        self.move(0, 3)


class IBlock(Block):
    def __init__(self):
        super().__init__(id=3)
        self.cells = {
            0: [Position(1, 0), Position(1, 1), Position(1, 2), Position(1, 3)],
            1: [Position(0, 2), Position(1, 2), Position(2, 2), Position(3, 2)],
            2: [Position(2, 0), Position(2, 1), Position(2, 2), Position(2, 3)],
            3: [Position(0, 1), Position(1, 1), Position(2, 1), Position(3, 1)]
        }
        self.move(-1, 3)


class OBlock(Block):
    def __init__(self):
        super().__init__(id=4)
        self.cells = {
            0: [Position(0, 0), Position(0, 1), Position(1, 0), Position(1, 1)]
        }
        self.move(0, 4)


class SBlock(Block):
    def __init__(self):
        super().__init__(id=5)
        self.cells = {
            0: [Position(0, 1), Position(0, 2), Position(1, 0), Position(1, 1)],
            1: [Position(0, 1), Position(1, 1), Position(1, 2), Position(2, 2)],
            2: [Position(1, 1), Position(1, 2), Position(2, 0), Position(2, 1)],
            3: [Position(0, 0), Position(1, 0), Position(1, 1), Position(2, 1)]
        }
        self.move(0, 3)


class TBlock(Block):
    def __init__(self):
        super().__init__(id=6)
        self.cells = {
            0: [Position(0, 1), Position(1, 0), Position(1, 1), Position(1, 2)],
            1: [Position(0, 1), Position(1, 1), Position(1, 2), Position(2, 1)],
            2: [Position(1, 0), Position(1, 1), Position(1, 2), Position(2, 1)],
            3: [Position(0, 1), Position(1, 0), Position(1, 1), Position(2, 1)]
        }
        self.move(0, 3)


class ZBlock(Block):
    def __init__(self):
        super().__init__(id=7)
        self.cells = {
            0: [Position(0, 0), Position(0, 1), Position(1, 1), Position(1, 2)],
            1: [Position(0, 2), Position(1, 1), Position(1, 2), Position(2, 1)],
            2: [Position(1, 0), Position(1, 1), Position(2, 1), Position(2, 2)],
            3: [Position(0, 1), Position(1, 0), Position(1, 1), Position(2, 0)]
        }
        self.move(0, 3)


class Grid:
    def __init__(self):
        self.num_rows = 20
        self.num_cols = 10
        self.cell_size = 30
        self.grid = [[0 for j in range(self.num_cols)] for i in range(self.num_rows)]
        self.colors = Colors.get_cell_colors()

    def print_grid(self):
        for row in range(self.num_rows):
            for column in range(self.num_cols):
                print(self.grid[row][column], end=" ")
            print()

    def is_inside(self, row, column):
        if row >= 0 and row < self.num_rows and column >= 0 and column < self.num_cols:
            return True
        return False

    def is_empty(self, row, column):
        if self.grid[row][column] == 0:
            return True
        return False

    def is_row_full(self, row):
        for column in range(self.num_cols):
            if self.grid[row][column] == 0:
                return False
        return True

    def clear_row(self, row):
        for column in range(self.num_cols):
            self.grid[row][column] = 0

    def move_row_down(self, row, num_rows):
        for column in range(self.num_cols):
            self.grid[row + num_rows][column] = self.grid[row][column]
            self.grid[row][column] = 0

    def clear_full_rows(self):
        completed = 0
        for row in range(self.num_rows - 1, 0, -1):
            if self.is_row_full(row):
                self.clear_row(row)
                completed += 1
            elif completed > 0:
                self.move_row_down(row, completed)
        return completed

    def reset(self):
        for row in range(self.num_rows):
            for column in range(self.num_cols):
                self.grid[row][column] = 0

    def draw(self, screen):
        for row in range(self.num_rows):
            for column in range(self.num_cols):
                cell_value = self.grid[row][column]
                x = column * self.cell_size + 11
                y = row * self.cell_size + 11
                if cell_value == 0:
                    pygame.draw.rect(screen, Colors.dark_grey, (x, y, self.cell_size - 1, self.cell_size - 1))
                else:
                    screen.blit(SPRITES[cell_value], (x, y))


class Game:
    def __init__(self):
        self.grid = Grid()
        self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
        self.current_block = self.get_random_block()
        self.next_block = self.get_random_block()
        self.game_over = False
        self.score = 0
        self.rotate_sound = pygame.mixer.Sound("rotate_sound.mp3")
        self.clear_sound = pygame.mixer.Sound("clear_sound.mp3")

        pygame.mixer.music.load("1.mp3")
        pygame.mixer.music.play(-1)

    def update_score(self, lines_cleared, move_down_points):
        if lines_cleared == 1:
            self.score += 100
        elif lines_cleared == 2:
            self.score += 300
        elif lines_cleared == 3:
            self.score += 500
        self.score += move_down_points

    def get_random_block(self):
        if len(self.blocks) == 0:
            self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
        block = random.choice(self.blocks)
        self.blocks.remove(block)
        return block

    def move_left(self):
        self.current_block.move(0, -1)
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.move(0, 1)

    def move_right(self):
        self.current_block.move(0, 1)
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.move(0, -1)

    def move_down(self):
        self.current_block.move(1, 0)
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.move(-1, 0)
            self.lock_block()

    def lock_block(self):
        tiles = self.current_block.get_cell_positions()
        for position in tiles:
            self.grid.grid[position.row][position.column] = self.current_block.id
        self.current_block = self.next_block
        self.next_block = self.get_random_block()
        rows_cleared = self.grid.clear_full_rows()
        if rows_cleared > 0:
            self.clear_sound.play()
            self.update_score(rows_cleared, 0)
        if self.block_fits() == False:
            self.game_over = True

    def reset(self):
        self.grid.reset()
        self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
        self.current_block = self.get_random_block()
        self.next_block = self.get_random_block()
        self.score = 0
        self.game_over = False

    def block_fits(self):
        tiles = self.current_block.get_cell_positions()
        for tile in tiles:
            if self.grid.is_empty(tile.row, tile.column) == False:
                return False
        return True

    def rotate(self):
        self.current_block.rotate()
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.undo_rotation()
        else:
            self.rotate_sound.play()

    def block_inside(self):
        tiles = self.current_block.get_cell_positions()
        for tile in tiles:
            if self.grid.is_inside(tile.row, tile.column) == False:
                return False
        return True

    def draw(self, screen):
        self.grid.draw(screen)
        self.current_block.draw(screen, 11, 11)

        if self.next_block.id == 3:
            self.next_block.draw(screen, 255, 290)
        elif self.next_block.id == 4:
            self.next_block.draw(screen, 255, 280)
        else:
            self.next_block.draw(screen, 270, 270)


# Инициализация pygame
pygame.init()

SPRITE_SIZE = 30  # Размер одного блока
SPRITE_SHEET = pygame.image.load("tetris_sprites.png")

# Координаты фигур на спрайт-листе (порядок: I, O, T, L, J, S, Z)
SPRITE_POSITIONS = {
    1: (0, 0),  # L
    2: (30, 0),  # J
    3: (60, 0),  # I
    4: (90, 0),  # O
    5: (120, 0),  # S
    6: (150, 0),  # T
    7: (180, 0)  # Z
}

# Вырезаем спрайты и сохраняем в словарь
SPRITES = {}

for key, (x, y) in SPRITE_POSITIONS.items():
    sprite = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
    sprite.blit(SPRITE_SHEET, (0, 0), (x, y, SPRITE_SIZE, SPRITE_SIZE))
    SPRITES[key] = sprite

# Настройки экрана
WIDTH, HEIGHT = 540, 620
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Тетрис")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
DARK_BLUE = (30, 90, 160)
LIGHT_BLUE = (70, 150, 230)
YELLOW = (255, 204, 0)
ORANGE = (255, 140, 0)
RED = (220, 20, 60)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)
BLUE = (50, 120, 200)
TRACK_COLOR = (100, 100, 100)
HOVER_COLOR = (255, 80, 80)
SLIDER_COLOR = (200, 50, 50)

# Шрифты
font = pygame.font.Font(None, 50)
button_font = pygame.font.Font(None, 40)
title_font = pygame.font.Font(None, 50)

# Глобальные переменные
current_complexity = 0
current_music = 0
current_volume = 0.5
music_playing = True
paused = False
start_time = 0
score = 0
rating_mode = False
nickname = ""

# Тексты и кнопки
title_text = font.render("Тетрис", True, DARK_BLUE)
title_rect = title_text.get_rect(center=(WIDTH // 2 + 40, 100))

start_button_text = button_font.render("Начать игру", True, WHITE)
start_button_rect = pygame.Rect(WIDTH // 2 - 100, 150, 270, 50)

rating_button_text = button_font.render("Игра на рейтинг", True, WHITE)
rating_button_rect = pygame.Rect(WIDTH // 2 - 100, 220, 270, 50)

quit_button_text = button_font.render("Выйти", True, WHITE)
quit_button_rect = pygame.Rect(WIDTH // 2 - 100, 290, 270, 50)

complexity_button_rect = pygame.Rect(WIDTH // 2 - 100, 360, 270, 50)
complexity_levels = [("Легко", YELLOW), ("Средне", ORANGE), ("Сложно", RED), ("Очень сложно", BLUE),
                     ("Невозможно", PURPLE)]

music_button_rect = pygame.Rect(WIDTH // 2 - 100, 430, 270, 50)
music_tracks = ["1.mp3", "2.mp3"]  # Убедитесь, что эти файлы существуют

volume_slider_rect = pygame.Rect(WIDTH // 2 - 100, 500, 270, 10)

# Инициализация музыки
pygame.mixer.music.load(music_tracks[current_music])
pygame.mixer.music.set_volume(current_volume)
pygame.mixer.music.play(-1)

# Тексты и кнопки
statistics_button_text = button_font.render("Статистика", True, WHITE)
statistics_button_rect = pygame.Rect(WIDTH // 2 - 100, 530, 270, 50)  # Переместим сложность и музыку ниже


# Ползунок громкости
slider_x = WIDTH // 2
slider_y = 500
slider_radius = 12
min_x, max_x = WIDTH // 2 - 100, WIDTH // 2 + 100
slider_dragging = False

# Функция для отображения таймера
def draw_timer(screen, start_time):
    current_time = pygame.time.get_ticks() - start_time
    seconds = current_time // 1000
    minutes = seconds // 60
    seconds %= 60
    timer_text = f"{minutes:02}:{seconds:02}"
    timer_surface = button_font.render(timer_text, True, WHITE)
    screen.blit(timer_surface, (WIDTH - 170, 140))


# Функция для отображения кнопок
def draw_buttons(screen):
    pause_button_rect = pygame.Rect(320, 400, 170, 50)
    continue_button_rect = pygame.Rect(320, 460, 170, 50)
    change_music_button_rect = pygame.Rect(320, 520, 170, 50)

    pygame.draw.rect(screen, LIGHT_BLUE, pause_button_rect, border_radius=10)
    pygame.draw.rect(screen, LIGHT_BLUE, continue_button_rect, border_radius=10)
    pygame.draw.rect(screen, LIGHT_BLUE, change_music_button_rect, border_radius=10)

    pause_text = button_font.render("Пауза", True, WHITE)
    continue_text = button_font.render("Продолжить", True, WHITE)
    change_music_text = button_font.render("Музыка", True, WHITE)

    screen.blit(pause_text, pause_text.get_rect(center=pause_button_rect.center))
    screen.blit(continue_text, continue_text.get_rect(center=continue_button_rect.center))
    screen.blit(change_music_text, change_music_text.get_rect(center=change_music_button_rect.center))

    return pause_button_rect, continue_button_rect, change_music_button_rect


# Главное меню
def main_menu():
    global rating_mode, nickname, current_complexity, current_volume, current_music

    running = True
    dragging = False  # Флаг для перетаскивания ползунка

    while running:
        screen.fill(GRAY)
        screen.blit(title_text, title_rect)

        # Рисуем кнопки
        pygame.draw.rect(screen, DARK_BLUE, start_button_rect, border_radius=10)
        pygame.draw.rect(screen, DARK_BLUE, rating_button_rect, border_radius=10)
        pygame.draw.rect(screen, DARK_BLUE, quit_button_rect, border_radius=10)
        pygame.draw.rect(screen, DARK_BLUE, statistics_button_rect, border_radius=10)  # Кнопка "Статистика"
        pygame.draw.rect(screen, complexity_levels[current_complexity][1], complexity_button_rect, border_radius=10)
        pygame.draw.rect(screen, DARK_BLUE, music_button_rect, border_radius=10)

        # Рисуем дорожку громкости
        pygame.draw.line(screen, TRACK_COLOR, (volume_slider_rect.x, volume_slider_rect.y + 5),
                         (volume_slider_rect.x + 200, volume_slider_rect.y + 5), 6)

        # Отображаем уровень громкости
        volume_text = font.render(f"{int(current_volume * 100)}%", True, WHITE)
        screen.blit(volume_text, (volume_slider_rect.x + 210, volume_slider_rect.y - 10))

        # Определяем координаты ползунка
        slider_x = volume_slider_rect.x + int(current_volume * 200)
        slider_y = volume_slider_rect.y + 5

        # Подсветка ползунка при наведении
        mouse_x, mouse_y = pygame.mouse.get_pos()
        color = HOVER_COLOR if dragging or (slider_x - 15 < mouse_x < slider_x + 15 and slider_y - 15 < mouse_y < slider_y + 15) else SLIDER_COLOR

        # Рисуем ползунок
        pygame.draw.circle(screen, color, (slider_x, slider_y), 12)


        # Отображение текста кнопок
        screen.blit(start_button_text, start_button_text.get_rect(center=start_button_rect.center))
        screen.blit(rating_button_text, rating_button_text.get_rect(center=rating_button_rect.center))
        screen.blit(quit_button_text, quit_button_text.get_rect(center=quit_button_rect.center))
        screen.blit(statistics_button_text,
                    statistics_button_text.get_rect(center=statistics_button_rect.center))  # Текст кнопки "Статистика"

        complexity_text = button_font.render(complexity_levels[current_complexity][0], True, WHITE)
        screen.blit(complexity_text, complexity_text.get_rect(center=complexity_button_rect.center))

        music_text = button_font.render(f"Музыка: {music_tracks[current_music]}", True, WHITE)
        screen.blit(music_text, music_text.get_rect(center=music_button_rect.center))

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    if start_button_rect.collidepoint(event.pos):
                        return "start"
                    if rating_button_rect.collidepoint(event.pos):
                        nickname = input_nickname()
                        if nickname:
                            rating_mode = True
                            return "start"
                    if quit_button_rect.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                    if statistics_button_rect.collidepoint(event.pos):  # Обработка нажатия на "Статистика"
                        statistics_and_search()
                    if complexity_button_rect.collidepoint(event.pos):
                        current_complexity = (current_complexity + 1) % len(complexity_levels)
                    if music_button_rect.collidepoint(event.pos):
                        current_music = (current_music + 1) % len(music_tracks)
                        pygame.mixer.music.load(music_tracks[current_music])
                        pygame.mixer.music.play(-1)
                    if (slider_x - 12 <= event.pos[0] <= slider_x + 12) and (slider_y - 12 <= event.pos[1] <= slider_y + 12):
                        dragging = True  # Начинаем перетаскивание

            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False  # Завершаем перетаскивание

            if event.type == pygame.MOUSEMOTION:
                if dragging:
                    current_volume = (event.pos[0] - volume_slider_rect.x) / 200
                    current_volume = max(0, min(1, current_volume))
                    pygame.mixer.music.set_volume(current_volume)

        pygame.display.flip()



# Ввод никнейма
def input_nickname():
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 300, 50)
    cancel_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
    continue_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50)

    color_inactive = LIGHT_BLUE
    color_active = DARK_BLUE
    color = color_inactive
    active = False
    text = ""
    font = pygame.font.Font(None, 40)

    while True:
        screen.fill(GRAY)

        # Заголовок
        title_text = font.render("Введите имя, чтобы продолжить", True, WHITE)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))

        # Ввод имени
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 20)
        input_box.w = width
        pygame.draw.rect(screen, color, input_box, 2)
        screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))

        # Кнопки
        pygame.draw.rect(screen, DARK_BLUE, cancel_button, border_radius=10)
        pygame.draw.rect(screen, LIGHT_BLUE, continue_button, border_radius=10)

        cancel_text = font.render("Отмена", True, WHITE)
        continue_text = font.render("Продолжить", True, WHITE)

        screen.blit(cancel_text, cancel_text.get_rect(center=cancel_button.center))
        screen.blit(continue_text, continue_text.get_rect(center=continue_button.center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                    color = color_active
                else:
                    active = False
                    color = color_inactive

                if cancel_button.collidepoint(event.pos):
                    return ""  # Пользователь отменил ввод

                if continue_button.collidepoint(event.pos):
                    return text.strip() if text.strip() else ""

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text.strip()
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif len(text) < 10:  # Ограничение длины имени
                        text += event.unicode

        pygame.display.flip()


def game_loop():
    global score, paused, start_time, current_music, nickname, current_complexity

    # Настройка шрифтов и текста
    title_font = pygame.font.Font(None, 40)
    score_surface = title_font.render("Счет", True, WHITE)
    next_surface = title_font.render("Следующий", True, WHITE)
    game_over_surface = pygame.font.Font(None, 70).render("ИГРА ОКОНЧЕНА", True, WHITE, DARK_BLUE)

    # Прямоугольники интерфейса
    score_rect = pygame.Rect(320, 55, 170, 60)
    next_rect = pygame.Rect(320, 215, 170, 180)

    # Перезапуск экрана и настройка игры
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Тетрис")

    clock = pygame.time.Clock()
    game = Game()  # Инициализация игрового объекта

    game_speed = 500 - (current_complexity + 1) * 80  # Скорость падения (600 → 100 мс)
    GAME_UPDATE = pygame.USEREVENT
    pygame.time.set_timer(GAME_UPDATE, game_speed)

    start_time = pygame.time.get_ticks()
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game.game_over:  # Перезапуск при нажатии клавиши
                    game.game_over = False
                    game.reset()
                    start_time = pygame.time.get_ticks()
                if not paused and not game.game_over:
                    if event.key == pygame.K_LEFT:
                        game.move_left()
                    if event.key == pygame.K_RIGHT:
                        game.move_right()
                    if event.key == pygame.K_DOWN:
                        game.move_down()
                        game.update_score(0, 1)
                    if event.key == pygame.K_UP:
                        game.rotate()
                if event.key == pygame.K_ESCAPE:
                    return "menu"  # Выход в меню

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pause_button_rect.collidepoint(event.pos):
                    paused = not paused
                if continue_button_rect.collidepoint(event.pos):
                    paused = False
                if change_music_button_rect.collidepoint(event.pos):
                    current_music = (current_music + 1) % len(music_tracks)
                    pygame.mixer.music.load(music_tracks[current_music])
                    pygame.mixer.music.play(-1)

            if event.type == GAME_UPDATE and not paused and not game.game_over:
                game.move_down()

        # === Отрисовка экрана ===
        screen.fill(DARK_BLUE)

        if game.game_over:
            result = game_over_screen(nickname, game.score, start_time)
            if result == "restart":
                game.reset()
                start_time = pygame.time.get_ticks()
                continue
            elif result == "menu":
                return "menu"

        # === Отображение счетчика очков ===
        pygame.draw.rect(screen, LIGHT_BLUE, score_rect, 0, 10)
        score_value_surface = title_font.render(str(game.score), True, WHITE)
        screen.blit(score_value_surface, score_value_surface.get_rect(center=score_rect.center))

        # === Отображение поля следующей фигуры ===
        pygame.draw.rect(screen, LIGHT_BLUE, next_rect, 0, 10)

        # === Отрисовка игрового процесса ===
        game.draw(screen)

        # === Отображение таймера и кнопок ===
        if not game.game_over:
            screen.blit(score_surface, (365, 20))
            screen.blit(next_surface, (320, 180))
            draw_timer(screen, start_time)

        pause_button_rect, continue_button_rect, change_music_button_rect = draw_buttons(screen)

        pygame.display.update()
        clock.tick(60)


def save_statistik(player_name, score, time):
    # Открытие (или создание) базы данных
    conn = sqlite3.connect('game_statistics.db')
    cursor = conn.cursor()

    # Создание таблицы, если она не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            player_name TEXT PRIMARY KEY,
            games_played INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            best_score INTEGER DEFAULT 0,
            total_time INTEGER DEFAULT 0
        )
    ''')
    # Проверяем, существует ли пользователь
    cursor.execute('SELECT * FROM statistics WHERE player_name = ?', (player_name,))
    player = cursor.fetchone()

    if player:
        # Если игрок уже существует, обновляем его данные
        games_played, total_score, best_score, total_time = player[1], player[2], player[3], player[4]

        games_played += 1
        total_score += score
        best_score = max(best_score, score)
        total_time += time

        # Обновляем данные игрока в базе данных
        cursor.execute('''
            UPDATE statistics
            SET games_played = ?, total_score = ?, best_score = ?, total_time = ?
            WHERE player_name = ?
        ''', (games_played, total_score, best_score, total_time, player_name))

    else:
        # Если игрока нет, добавляем его в базу данных
        cursor.execute('''
            INSERT INTO statistics (player_name, games_played, total_score, best_score, total_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (player_name, 1, score, score, time))
    # Сохраняем изменения и закрываем соединение с базой данных
    conn.commit()
    conn.close()


def statistics_and_search():
    # Открытие базы данных
    conn = sqlite3.connect('game_statistics.db')
    cursor = conn.cursor()
    # Получение лучшего игрока
    cursor.execute('SELECT player_name, best_score FROM statistics ORDER BY best_score DESC LIMIT 1')
    best_player = cursor.fetchone()
    conn.close()
    running = True
    clock = pygame.time.Clock()
    search_text = ""
    search_results = None
    y_offset = 140
    max_height = HEIGHT - 100  # Ограничение по высоте для статистики
    max_width = 520  # Ограничение по ширине для текста

    small_font = pygame.font.SysFont("Arial", 28)
    background_color = GRAY  # Серый фон

    def search_player():
        """Функция для поиска игрока в базе данных."""
        nonlocal search_results
        if search_text.strip() == "":
            search_results = None
            return
        conn = sqlite3.connect('game_statistics.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT player_name, games_played, total_score, best_score, total_time FROM statistics WHERE player_name = ?',
            (search_text,))
        search_results = cursor.fetchone()
        conn.close()

    while running:
        screen.fill(background_color)

        # Заголовок
        title_surface = title_font.render("Статистика игры", True, LIGHT_BLUE)
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 20))

        # Лучший игрок
        if best_player:
            best_player_surface = small_font.render(f"Лучший игрок: {best_player[0]}    Результат: {best_player[1]}",
                                                    True, GREEN)
            screen.blit(best_player_surface, (20, 80))

        # Отображение результатов поиска, если они есть
        if search_results:
            y_offset = 160
            search_surface = small_font.render(f"Результаты для {search_results[0]}:", True, LIGHT_BLUE)
            screen.blit(search_surface, (20, y_offset))
            y_offset += 40

            search_player_name = search_results[0]
            games_played = search_results[1]
            total_score = search_results[2]
            best_score = search_results[3]
            total_time = search_results[4]

            avg_score = total_score / games_played if games_played > 0 else 0
            avg_time = total_time / games_played if games_played > 0 else 0

            search_stats = [
                f"Игрок: {search_player_name}",
                f"Игры: {games_played}",
                f"Средний Результат: {avg_score:.2f}",
                f"Лучший: {best_score}",
                f"Среднее Время: {avg_time:.2f} сек."
            ]

            for stat in search_stats:
                stat_surface = small_font.render(stat, True, LIGHT_BLUE)
                screen.blit(stat_surface, (20, y_offset))
                y_offset += stat_surface.get_height()

        # Поле для ввода текста поиска
        search_box_rect = pygame.Rect(20, HEIGHT - 100, 400, 40)
        pygame.draw.rect(screen, WHITE, search_box_rect, border_radius=10)
        search_text_surface = small_font.render(search_text, True, BLUE)
        screen.blit(search_text_surface, (search_box_rect.x + 5, search_box_rect.y + 5))

        # Кнопка "Поиск"
        search_button_rect = pygame.Rect(430, HEIGHT - 100, 90, 40)
        pygame.draw.rect(screen, GREEN, search_button_rect, border_radius=10)
        search_button_text = button_font.render("Поиск", True, WHITE)
        screen.blit(search_button_text, search_button_text.get_rect(center=search_button_rect.center))

        # Кнопка "Назад"
        back_button_rect = pygame.Rect(WIDTH - 120, HEIGHT - 50, 100, 40)
        pygame.draw.rect(screen, DARK_BLUE, back_button_rect, border_radius=10)
        back_text = button_font.render("Назад", True, WHITE)
        screen.blit(back_text, back_text.get_rect(center=back_button_rect.center))

        pygame.display.update()
        clock.tick(60)

        # Обработка нажатий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    search_text = search_text[:-1]
                elif event.key == pygame.K_RETURN:
                    search_player()
                else:
                    search_text += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    running = False
                if search_button_rect.collidepoint(event.pos):
                    search_player()


def game_over_screen(player_name, score, start_time):
    global rating_mode
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    if rating_mode:
        save_statistik(player_name, score, elapsed_time)

    while True:
        screen.fill(GRAY)

        # Текст "Игра окончена"
        game_over_text = font.render("Игра окончена", True, RED)
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        screen.blit(game_over_text, game_over_rect)

        # Итоговый счет
        final_score_text = button_font.render(f"Счет: {score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        screen.blit(final_score_text, final_score_rect)

        # Время в игре
        final_time_text = button_font.render(f"Время: {elapsed_time} сек", True, WHITE)
        final_time_rect = final_time_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        screen.blit(final_time_text, final_time_rect)

        # Кнопка "Заново"
        restart_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50)
        pygame.draw.rect(screen, DARK_BLUE, restart_button_rect, border_radius=10)
        restart_text = button_font.render("Заново", True, WHITE)
        screen.blit(restart_text, restart_text.get_rect(center=restart_button_rect.center))

        # Кнопка "В меню"
        menu_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50)
        pygame.draw.rect(screen, DARK_BLUE, menu_button_rect, border_radius=10)
        menu_text = button_font.render("В меню", True, WHITE)
        screen.blit(menu_text, menu_text.get_rect(center=menu_button_rect.center))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button_rect.collidepoint(event.pos):
                    return "restart"  # Возвращаем "restart" для перезапуска игры
                if menu_button_rect.collidepoint(event.pos):
                    rating_mode = False
                    return "menu"  # Возвращаем "menu" для возврата в главное меню


# Основной цикл
def main():
    while True:
        action = main_menu()
        if action == "start":
            while True:  # Внутренний цикл для игры
                result = game_loop()
                if result == "menu":
                    break  # Выход в главное меню
                elif result == "game_over":
                    # Переход на экран завершения игры
                    restart_action = game_over_screen(nickname, score, start_time)
                    if restart_action == "restart":
                        continue  # Перезапуск игры
                    elif restart_action == "menu":
                        break  # Выход в главное меню
        elif action == "game_over":
            result = game_over_screen(nickname, score, start_time)
            if result == "menu":
                continue


if __name__ == "__main__":
    main()
