"""Модуль содержит общую логику для игры "Змейка".

Правила игры: Змейка (цвет по умолчанию - зелёный) движется в одном из
четырёх направлений - вверх, вниз, влево или вправо. Игрок управляет
направлением её движения, но змейка не может остановиться или двигаться назад.
Каждый раз, когда змейка съедает яблоко (цвет по умолчанию - красный),
она увеличивается в длину на один сегмент. При этом, положение яблока случайно
меняется. Змейка может проходить сквозь одну стену и появляться
с противоположной стороны поля. Если змейка столкнётся сама с собой, то змейка
сбрасывается до начального состояния.

Дополнительно: реализована генерация "неправильного продукта" (цвет
по умолчанию - оранжевый). Если змейка съест яблоко - положение яблока случайно
меняется. Если змейка съест неправильный продукт - змейка сбрасывается до
начального состояния. При этом, положение неправильного продукта случайно
меняется.

Управление:
    - Изменение направления движения змейки: клавиши-стрелки Вверх, Вниз,
        Влево, Вправо.
    - Изменение скорости движения змейки: клавиши от 1 до 9 включительно,
        где 1 - самая низкая скорость, 9 - самая высокая скорость.
    - Выход из игры: клавиша Esc.

Классы:
    GameObject: Базовый класс для игровых объектов.
    Snake: Класс для представления объекта "Змейка" в игре "Змейка".
    Apple: Класс для представления объекта "Яблоко" в игре "Змейка".
    WrongProduct: Класс для представления объекта "Неправильный продукт" в
        игре "Змейка".

Функции:
    handle_keys: Обрабатывает нажатия клавиш пользователем.
    main: Запускает игру "Змейка".
"""
from random import choice, randint
from typing import Optional
import sys

import pygame as pg

# Инициализация PyGame.
pg.init()

# Настройка заголовка.
TITLE = ('ЗМЕЙКА. Макс. длина: {max_length}. '
         + 'Скорость: {speed} (Клав. 1 - 9) | '
         + '(Выход: ESC)')

# Константы для размеров.
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения.
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Словарь с привязкой текущего направления движения змейки и клавиш
# клавиатуры со следующим направлением движения змейки.
NEW_DIRECTION = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT
}

# Словарь с привязкой цифровых клавиш клавиатуры
# к скорости движения змейки.
SNAKE_SPEED = {
    pg.K_1: 1,
    pg.K_2: 2,
    pg.K_3: 3,
    pg.K_4: 4,
    pg.K_5: 5,
    pg.K_6: 6,
    pg.K_7: 7,
    pg.K_8: 8,
    pg.K_9: 9
}

# Цвета фона - светло-серый.
BOARD_BACKGROUND_COLOR = (211, 211, 211)

# Цвет границы ячейки.
CELL_BOUNDARY_COLOR = (93, 216, 228)

# Цвет яблока - красный.
APPLE_COLOR = (255, 0, 0)

# Цвет неправильного продукта - оранжевый.
WRONG_PRODUCT_COLOR = (255, 165, 0)

# Цвет змейки - зелёный.
SNAKE_COLOR = (76, 187, 23)

# Центральная точка экрана.
CENTER_SCREEN_POINT = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

# Настройка игрового окна.
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
screen.fill(BOARD_BACKGROUND_COLOR)
pg.display.flip()

# Настройка времени.
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов.

    Атрибуты:
        position: Позиция объекта на игровом поле. Инициализируется
            как центральная точка экрана.
        body_color: Цвет объекта. По умолчанию - BOARD_BACKGROUND_COLOR.
    """

    def __init__(self,
                 body_color: tuple[int, ...] = BOARD_BACKGROUND_COLOR) -> None:
        self.position: tuple[int, int] = CENTER_SCREEN_POINT
        self.body_color: tuple[int, ...] = body_color

    def draw_cell(self, position: tuple[int, int],
                  cell_color: Optional[tuple[int, ...]] = None) -> None:
        """Отрисовывает ячейку объекта на экране.

        Параметры:
            position: Позиция объекта на игровом поле.
            cell_color: Цвет ячейки.
        """
        cell_boundary_color = cell_color if cell_color else CELL_BOUNDARY_COLOR
        cell_color = cell_color if cell_color else self.body_color
        rect = pg.Rect(
            (position[0], position[1]), (GRID_SIZE, GRID_SIZE)
        )
        pg.draw.rect(screen, cell_color, rect)
        pg.draw.rect(screen, cell_boundary_color, rect, 1)

    def draw(self) -> None:
        """Отрисовывает объект на экране."""
        raise AttributeError('Игровой объект не имеет атрибут draw')


class Snake(GameObject):
    """Класс для представления объекта "Змейка" в игре "Змейка".
    Наследуется от класса GameObject.

    Атрибуты:
        length: Длина объекта "Змейка". Инициализируется значением 1.
        positions: Список, содержащий позиции всех сегментов тела объекта
            "Змейка". Инициализируется с позицией головы (первого элемента
            списка positions) в центре экрана.
        direction: Направление движения объекта "Змейка". Инициализируется
            кортежем, содержащим численное представление направления движения.
        speed: Скорость движения объекта "Змейка". Инициализируется
            значением 5.
        max_length: Максимальная величина змейки за игру. Инициализируется
            значением 1.
        last: Позиция последнего сегмента объекта "Змейка" (последнего элемента
            списка positions). Инициализируется значением None.
        reset_situation: Проверка сброса объекта "Змейка".
    """

    def __init__(self,
                 body_color: tuple[int, ...] = SNAKE_COLOR) -> None:
        super().__init__(body_color)
        self.reset()
        self.speed = 5
        self.max_length = 1
        self.last: Optional[tuple[int, int]] = None
        self.reset_situation = False

    def reset(self) -> None:
        """Сбрасывает объект "Змейка" в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice((UP, DOWN, RIGHT, LEFT))

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает позицию головы объекта "Змейка"."""
        return self.positions[0]

    def move(self) -> None:
        """Обновляет позицию объекта "Змейка"."""
        current_head_position = self.get_head_position()
        # Определение новой позиции головы.
        next_head_position = (
            (current_head_position[0] + self.direction[0] * GRID_SIZE)
            % SCREEN_WIDTH,
            (current_head_position[1] + self.direction[1] * GRID_SIZE)
            % SCREEN_HEIGHT
        )
        # Проверка на столкновение с собой.
        if next_head_position in self.positions:
            self.reset_situation = True
        # Обновление списка позиций.
        else:
            self.positions.insert(0, next_head_position)
        # Проверка текущей длины змеи
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def update_direction(self, event_key: int) -> None:
        """Обновляет направление движения объекта "Змейка".

        Параметры:
            event_key: Клавиша клавиатуры.
        """
        self.direction = NEW_DIRECTION.get((self.direction, event_key),
                                           self.direction)

    def update_speed(self, event_key: int) -> None:
        """Обновляет скорость движения объекта "Змейка".

        Параметры:
            event_key: Клавиша клавиатуры.
        """
        self.speed = SNAKE_SPEED.get(event_key, self.speed)

    def update_max_length(self):
        """Обновляет максимальную длину объекта "Змейка" за игру."""
        self.max_length = max(self.length, self.max_length)

    def draw(self) -> None:
        """Отрисовывает объект на экране."""
        self.draw_cell(self.get_head_position())
        # Затирание старой позиции хвоста змейки.
        self.draw_cell(self.last,
                       cell_color=BOARD_BACKGROUND_COLOR)


class Apple(GameObject):
    """Класс для представления объекта "Яблоко" в игре "Змейка".
    Наследуется от класса GameObject.

    Атрибуты:
        hold_positions: Занятые ячейки. Инициализируется при создании
            объекта класса. По умолчанию - [CENTER_SCREEN_POINT].
    """

    def __init__(self,
                 hold_positions: list[tuple[int, int]] = [CENTER_SCREEN_POINT],
                 body_color: tuple[int, ...] = APPLE_COLOR) -> None:
        super().__init__(body_color)
        self.randomize_position(hold_positions)

    def randomize_position(self,
                           hold_positions: list[tuple[int, int]]) -> None:
        """Устанавливает случайное положение объекта-продукта на игровом поле.

        Параметры:
            hold_positions: Занятые ячейки.
        """
        while True:
            random_width = (randint(0, GRID_WIDTH - 1) * GRID_SIZE)
            random_height = (randint(0, GRID_HEIGHT - 1) * GRID_SIZE)
            if (random_width, random_height) not in hold_positions:
                self.position = (random_width, random_height)
                return

    def draw(self) -> None:
        """Отрисовывает объект на экране."""
        self.draw_cell(self.position)


class WrongProduct(Apple):
    """Класс для представления объекта "Неправильный продукт" в игре "Змейка".
    Наследуется от класса Apple.
    """

    def __init__(self,
                 hold_positions: list[tuple[int, int]] = [CENTER_SCREEN_POINT],
                 body_color: tuple[int, ...] = WRONG_PRODUCT_COLOR) -> None:
        super().__init__(hold_positions, body_color)


def handle_keys(snake_object: Snake) -> None:
    """Обрабатывает нажатия клавиш пользователем.
    Применяется для изменения направления движения объекта "Змейка" и
        изменения скорости её движения.

    Параметры:
        game_object: Объект класса Snake.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            # Выход из игры по клавише ESC.
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            # Обновление направления движения змейки.
            if event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                snake_object.update_direction(event.key)
            # Обновление скорости движения змейки.
            if event.key in (pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5,
                             pg.K_6, pg.K_7, pg.K_8, pg.K_9):
                snake_object.update_speed(event.key)


def main():
    """Запускает игру "Змейка"."""
    # Инициализация объектов классов.
    snake = Snake()
    apple = Apple(hold_positions=snake.positions)
    wrong_product = WrongProduct(hold_positions=(snake.positions
                                                 + [apple.position]))
    while True:
        # Замедление скорости движения змейки до SPEED раз в секунду.
        clock.tick(snake.speed)
        # Заголовок окна игрового поля.
        # Информация обновляется каждую итерацию.
        pg.display.set_caption(TITLE.format(max_length=snake.max_length,
                                            speed=snake.speed))
        # Обработка нажатий клавиш.
        handle_keys(snake)
        # Проверка, съедено ли яблоко.
        if snake.get_head_position() == apple.position:
            snake.length += 1
            snake.update_max_length()
            apple.randomize_position(snake.positions
                                     + [wrong_product.position])
        # Проверка, съеден ли неправильный продукт.
        elif snake.get_head_position() == wrong_product.position:
            snake.reset_situation = True
            wrong_product.randomize_position(snake.positions
                                             + [apple.position])
        # Проверка, должна ли быть сброшена змейка.
        if snake.reset_situation:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset_situation = False
        snake.move()
        apple.draw()
        wrong_product.draw()
        snake.draw()
        # Обновление дисплея.
        pg.display.update()


if __name__ == "__main__":
    main()
