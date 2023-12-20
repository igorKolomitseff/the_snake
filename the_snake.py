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

import pygame as pg

# Инициализация PyGame.
pg.init()

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

    Методы:
        draw: Отрисовывает объект на экране.
    """

    def __init__(self,
                 body_color: tuple[int, int, int] = BOARD_BACKGROUND_COLOR) -> None:  # noqa E501
        # Значение цвета объекта задаётся в инициализаторе по умолчанию.
        # Иначе тесты от Практикума будут падать.
        # Аналогично с дочерними классами.
        # Можно указать None, но тогда функция rect в функции draw будет
        # придираться к аннотации, так как она ожидает кортеж, но никак
        # не None. Это видно только при проверке типов с помощью MyPy.
        # Но на проверку pytest и flake8 от Практикума это никак
        # не влияет, всё проходит без ошибок.
        """Инициализирует атрибуты класса."""
        self.position: tuple[int, int] = CENTER_SCREEN_POINT
        self.body_color: tuple[int, int, int] = body_color

    def draw(self, position: tuple[int, int], surface: pg.Surface = screen,
             cell_color: Optional[tuple[int, int, int]] = None,
             cell_boundary_color: tuple[int, int, int] = CELL_BOUNDARY_COLOR) -> None:  # noqa E501
        """Отрисовывает объект на экране.

        Параметры:
            position: Позиция объекта на игровом поле.
            surface: Игровое окно.
            cell_color: Цвет игрового объекта.
            cell_boundary_color: Цвет границы ячейки игрового объекта.
        """
        cell_color = cell_color or self.body_color
        rect = pg.Rect(
            (position[0], position[1]), (GRID_SIZE, GRID_SIZE)
        )
        pg.draw.rect(surface, cell_color, rect)
        pg.draw.rect(surface, cell_boundary_color, rect, 1)


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

    Методы:
        get_head_position: Возвращает позицию головы (первого элемента списка
            positions) объекта "Змейка".
        move: Обновляет позицию объекта "Змейка".
        update_direction: Обновляет направление движения объекта "Змейка".
        update_speed: Обновляет скорость движения объекта "Змейка".
        update_max_length: Обновляет максимальную длину объекта "Змейка" за
            игру.
        reset: Сбрасывает объект "Змейка" в начальное состояние после
            столкновения с собой.
    """

    def __init__(self,
                 body_color: tuple[int, int, int] = BOARD_BACKGROUND_COLOR) -> None:  # noqa E501
        """Инициализирует объект класса."""
        super().__init__(body_color)
        self.length: int
        self.positions: list[tuple[int, int]]
        self.direction: tuple[int, int]
        self.length, self.positions, self.direction = self.reset()
        self.speed = 5
        self.max_length = 1
        self.last: Optional[tuple[int, int]] = None

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает позицию головы объекта "Змейка".

        Возвращает:
            Кортеж с координатами текущей позиции головы объекта "Змейка"
        """
        return self.positions[0]

    def move(self) -> None:
        """Обновляет позицию объекта "Змейка"."""
        # Текущее положение головы.
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
            # Обновление максимальной длины змейки.
            self.update_max_length()
            # Сброс змейки.
            self.reset()

            # Очистка экрана.
            screen.fill(BOARD_BACKGROUND_COLOR)

        # Обновление списка позиций.
        else:
            self.positions.insert(0, next_head_position)

        # Проверка текущей длины змеи
        if len(self.positions) > self.length:
            # Удаление последнего элемента змейки
            self.last = self.positions.pop()

    def update_direction(self, event_key: int) -> None:
        """Обновляет направление движения объекта "Змейка".

        Параметры:
            event_key: Клавиша клавиатуры.

        """
        self.direction = NEW_DIRECTION.get(
            (self.direction, event_key), self.direction)

    def update_speed(self, event_key: int) -> None:
        """Обновляет скорость движения объекта "Змейка".

        Параметры:
            event_key: Клавиша клавиатуры.
        """
        self.speed = SNAKE_SPEED.get(event_key, self.speed)

    def update_max_length(self):
        """Обновляет максимальную длину объекта "Змейка" за игру."""
        if self.max_length < self.length:
            self.max_length = self.length

    def reset(self) -> tuple[int, list[tuple[int, int]], tuple[int, int]]:
        """Сбрасывает объект "Змейка" в начальное состояние.

        Возвращает:
            Кортеж данных.
        """
        # Сброс длины змейки.
        self.length = 1

        # Сброс позиций змейки.
        self.positions = [self.position]

        # Изменение направления движения змейки.
        self.direction = choice((UP, DOWN, RIGHT, LEFT))

        return self.length, self.positions, self.direction


class Apple(GameObject):
    """Класс для представления объекта "Яблоко" в игре "Змейка".
    Наследуется от класса GameObject.

    Атрибуты:
        occupied_positions: Занятые ячейки. Инициализируется при создании
            объекта класса. По умолчанию - [CENTER_SCREEN_POINT].

    Методы:
        randomize_position: Устанавливает случайное положение объекта "Яблоко"
            на игровом поле.
        update_randomize_position: Обновляет положение объекта "Яблоко" на
            игровом поле.
    """

    def __init__(self, occupied_positions: list[tuple[int, int]] = [CENTER_SCREEN_POINT],  # noqa E501
                 body_color: tuple[int, int, int] = BOARD_BACKGROUND_COLOR) -> None:  # noqa E501
        # Применяются параметры со значением по умолчанию
        # из-за тестов Практикума.
        """Инициализирует объект класса."""
        super().__init__(body_color)
        self.position: tuple[int, int] = self.randomize_position(occupied_positions)  # noqa E501

    def randomize_position(self,
                           occupied_positions: list[tuple[int, int]]) -> tuple[int, int]:  # noqa E501
        """Устанавливает случайное положение объекта "Яблоко" на игровом поле.

        Параметры:
            occupied_positions: Занятые ячейки.

        Возвращает:
            Кортеж координат объекта "Яблоко".
        """
        # Определение случайных координат по ширине и высоте окна.
        while True:
            # Под координатами в данном случае подразумеваются координаты
            # верхнего левого угла ячейки. Функция randint выбирает случайное
            # число из переданного ей диапазона, включая правое значение.
            # Поэтому для предотвращения отображения объекта за пределами
            # правой границы экрана функции randint нужно передать
            # (размер сетки - 1)
            random_width = (randint(0, GRID_WIDTH - 1) * GRID_SIZE)
            random_height = (randint(0, GRID_HEIGHT - 1) * GRID_SIZE)

            if (random_width, random_height) not in occupied_positions:
                break

        return (random_width, random_height)

    def update_randomize_position(self,
                               occupied_positions: list[tuple[int, int]]) -> None:    # noqa E501
        """Обновляет положение объекта "Яблоко" на игровом поле.

        Параметры:
            occupied_positions: Занятые позиции.
        """
        self.position = self.randomize_position(occupied_positions)


class WrongProduct(Apple):
    """Класс для представления объекта "Неправильный продукт" в игре "Змейка".
    Наследуется от класса Apple.
    """

    def __init__(self, occupied_positions: list[tuple[int, int]] = [CENTER_SCREEN_POINT],  # noqa E501
                 body_color: tuple[int, int, int] = BOARD_BACKGROUND_COLOR) -> None:  # noqa E501
        """Инициализирует объект класса."""
        super().__init__(occupied_positions, body_color)


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

        elif event.type == pg.KEYDOWN:

            # Обновление направления движения змейки.
            if (snake_object.direction, event.key) in NEW_DIRECTION.keys():
                snake_object.update_direction(event.key)

            # Обновление скорости движения змейки.
            if event.key in SNAKE_SPEED.keys():
                snake_object.update_speed(event.key)

            # Выход из игры по клавише ESC.
            if event.key == pg.K_ESCAPE:
                pg.quit()


def main():
    """Запускает игру "Змейка"."""
    # Инициализация объектов классов.
    snake = Snake(body_color=SNAKE_COLOR)
    apple = Apple(occupied_positions=snake.positions,
                  body_color=APPLE_COLOR)
    wrong_product = WrongProduct(occupied_positions=(snake.positions
                                                     + [apple.position]),
                                 body_color=WRONG_PRODUCT_COLOR)

    while True:
        # Замедление скорости движения змейки до SPEED раз в секунду.
        clock.tick(snake.speed)

        # Заголовок окна игрового поля.
        # Информация обновляется каждую итерацию.
        pg.display.set_caption(f'ЗМЕЙКА.  Макс. длина: {snake.max_length}. '
                               f'Скорость: {snake.speed} (Клав. 1 - 9) | '
                               f'(Выход: ESC)')

        # Обработка нажатий клавиш.
        handle_keys(snake)

        # Проверка, съедено ли яблоко.
        if snake.get_head_position() == apple.position:
            # Увеличение длины змейки.
            snake.length += 1

            # Изменение положения яблока на игровом поле.
            apple.update_randomize_position(snake.positions
                                            + [wrong_product.position])

        # Проверка, съеден ли неправильный продукт.
        elif snake.get_head_position() == wrong_product.position:
            # Обновление максимальной длины змейки.
            snake.update_max_length()

            # Сброс змейки.
            snake.reset()

            # Изменение положения неправильного продукта на игровом поле.
            wrong_product.update_randomize_position(snake.positions
                                                    + [apple.position])

            # Очистка экрана.
            screen.fill(BOARD_BACKGROUND_COLOR)

        # Движение змейки.
        snake.move()

        # Отображение яблока.
        apple.draw(position=apple.position)

        # Отображение неправильного продукта.
        wrong_product.draw(position=wrong_product.position)

        # Отображение головы змейки.
        snake.draw(position=snake.get_head_position())

        # Затирание старой позиции хвоста змейки.
        snake.draw(position=snake.last,
                   cell_color=BOARD_BACKGROUND_COLOR,
                   cell_boundary_color=BOARD_BACKGROUND_COLOR)

        # Обновление дисплея.
        pg.display.update()


if __name__ == "__main__":
    main()
