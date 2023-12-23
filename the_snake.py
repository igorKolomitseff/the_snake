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
    - Изменение скорости движения змейки:
        левая или правая клавиша SHIFT - увеличение скорости змейки на 5
        единиц.
        левая или правая клавиша CTRL - уменьшение скорости змейки на 5
        единиц.
    - Выход из игры: клавиша Esc.
"""
from random import choice, randint
from typing import Optional
import sys

import pygame as pg

# Инициализация PyGame.
pg.init()

# Настройка заголовка.
TITLE = ('SNAKE. Max. length: {max_length}. '
         + 'Speed: {speed} (SHIFT ↑, CTRL ↓) |'
         + '(Exit: ESC)')

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
NEW_DIRECTIONS = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT
}
DIRECTION_CONTROL_BUTTONS = (
    pg.K_UP,
    pg.K_DOWN,
    pg.K_LEFT,
    pg.K_RIGHT
)

# Словарь с привязкой клавиш клавиатуры к ускорению
# скорости движения змейки.
SNAKE_ACCELERATIONS = {
    pg.K_LSHIFT: 1,
    pg.K_RSHIFT: 1,
    pg.K_LCTRL: -1,
    pg.K_RCTRL: -1
}
ACCELERATION_CONTROL_BUTTONS = (
    pg.K_LSHIFT,
    pg.K_RSHIFT,
    pg.K_LCTRL,
    pg.K_RCTRL
)


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

# Флаг для корректировки необходимости обновления информации в заголовке.
update_title_information = False


class GameObject:
    """Базовый класс для игровых объектов.

    Атрибуты:
        position: Позиция объекта на игровом поле.
        body_color: Цвет объекта.
    """

    def __init__(
        self,
        body_color: tuple[int, ...] = BOARD_BACKGROUND_COLOR
    ) -> None:
        self.position = CENTER_SCREEN_POINT
        self.body_color = body_color

    def draw_cell(
        self,
        position: tuple[int, ...],
        cell_color: Optional[tuple[int, ...]] = None
    ) -> None:
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
        raise NotImplementedError(f'{type(self).__name__} '
                                  f'не имеет реализации метода draw.')


class Snake(GameObject):
    """Класс для представления объекта "Змейка" в игре "Змейка".

    Атрибуты:
        length: Длина объекта "Змейка".
        positions: Список, содержащий позиции всех сегментов тела объекта
            "Змейка".
        direction: Направление движения объекта "Змейка".
        speed: Скорость движения объекта "Змейка".
        max_length: Максимальная величина змейки за игру.
        last: Позиция последнего сегмента объекта "Змейка".
        reset_situation: Проверка сброса объекта "Змейка".
    """

    MIN_SNAKE_SPEED = 5
    MAX_SNAKE_SPEED = 30

    def __init__(
        self,
        body_color: tuple[int, ...] = SNAKE_COLOR
    ) -> None:
        super().__init__(body_color)
        self.reset()
        self.speed = self.MIN_SNAKE_SPEED
        self.max_length = self.length
        self.last = None
        self.reset_situation = False

    def reset(self) -> None:
        """Сбрасывает объект "Змейка" в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice((UP, DOWN, RIGHT, LEFT))

    def get_head_position(self) -> tuple[int, ...]:
        """Возвращает позицию головы объекта "Змейка"."""
        return self.positions[0]

    def move(self) -> None:
        """Обновляет позицию объекта "Змейка"."""
        current_head_position = self.get_head_position()
        next_head_position = (
            (current_head_position[0] + self.direction[0] * GRID_SIZE)
            % SCREEN_WIDTH,
            (current_head_position[1] + self.direction[1] * GRID_SIZE)
            % SCREEN_HEIGHT
        )
        if next_head_position in self.positions:
            self.reset_situation = True
        else:
            self.positions.insert(0, next_head_position)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def update_direction(self, new_direction: tuple[int, ...]) -> None:
        """Обновляет направление движения объекта "Змейка".

        Параметры:
            next_direction: Новое направление движения объекта "Змейка".
        """
        self.direction = new_direction

    def update_speed(self, new_speed: int) -> None:
        """Обновляет скорость движения объекта "Змейка".

        Параметры:
            new_speed: Новая скорость объекта "Змейка".
        """
        if self.MIN_SNAKE_SPEED <= new_speed <= self.MAX_SNAKE_SPEED:
            self.speed = new_speed
            global update_title_information
            update_title_information = True

    def increase_length(self):
        """Увеличивает длину объекта "Змейка."""
        self.length += 1
        global update_title_information
        update_title_information = True

    def update_max_length(self):
        """Обновляет максимальную длину объекта "Змейка" за игру."""
        self.max_length = max(self.length, self.max_length)

    def draw(self) -> None:
        """Отрисовывает объект "Змейка" на экране."""
        self.draw_cell(self.get_head_position())
        # Затирание старой позиции хвоста змейки.
        self.draw_cell(position=self.last,
                       cell_color=BOARD_BACKGROUND_COLOR)


class Apple(GameObject):
    """Класс для представления объекта "Яблоко" в игре "Змейка".

    Атрибуты:
        hold_positions: Занятые ячейки.
    """

    def __init__(
        self,
        hold_positions: list[tuple[int, ...]] = [CENTER_SCREEN_POINT],
        body_color: tuple[int, ...] = APPLE_COLOR
    ) -> None:
        super().__init__(body_color)
        self.randomize_position(hold_positions)

    def randomize_position(
        self,
        hold_positions: list[tuple[int, ...]]
    ) -> None:
        """Устанавливает случайное положение объекта-продукта на игровом поле.

        Параметры:
            hold_positions: Занятые ячейки.
        """
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in hold_positions:
                return

    def draw(self) -> None:
        """Отрисовывает объект-продукт на экране."""
        self.draw_cell(self.position)


class WrongProduct(Apple):
    """Класс для представления объекта "Неправильный продукт"."""

    pass


def handle_keys(snake_object: Snake) -> None:
    """Обрабатывает нажатия клавиш пользователем.

    Параметры:
        game_object: Объект класса Snake.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN:
            # Выход из игры по клавише ESC.
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            # Обновление направления движения змейки.
            if event.key in DIRECTION_CONTROL_BUTTONS:
                snake_object.update_direction(
                    NEW_DIRECTIONS.get((snake_object.direction, event.key),
                                       snake_object.direction)
                )
            # Обновление скорости движения змейки.
            elif event.key in ACCELERATION_CONTROL_BUTTONS:
                snake_object.update_speed(
                    snake_object.speed + SNAKE_ACCELERATIONS[event.key]
                )


def main():
    """Запускает игру "Змейка"."""
    snake = Snake()
    apple = Apple(hold_positions=snake.positions)
    wrong_product = WrongProduct(
        body_color=WRONG_PRODUCT_COLOR,
        hold_positions=[*snake.positions, apple.position])

    global update_title_information
    update_title_information = True

    while True:
        clock.tick(snake.speed)
        # Проверка, нужно ли обновлять информацию в заголовке.
        if update_title_information:
            pg.display.set_caption(TITLE.format(max_length=snake.max_length,
                                                speed=snake.speed))
            update_title_information = False
        handle_keys(snake)
        # Проверка, съедено ли яблоко.
        if snake.get_head_position() == apple.position:
            snake.increase_length()
            snake.update_max_length()
            apple.randomize_position(
                [*snake.positions, wrong_product.position]
            )
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
        pg.display.update()


if __name__ == "__main__":
    main()
