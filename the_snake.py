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
по умолчанию - оранжевый). Если змейка съест яблоко - положения яблока и
неправильного продукта случайно меняются. Если змейка съест неправильный
продукт - змейка сбрасывается до начального состояния. При этом, положение
неправильного продукта случайно меняется.

Классы:
    GameObject: Базовый класс для игровых объектов.
    Apple: Класс для представления объекта "Яблоко" в игре "Змейка".
    WrongProduct: Класс для представления объекта "Неправильный продукт" в
        игре "Змейка".
    Snake: Класс для представления объекта "Змейка" в игре "Змейка".

Функции:
    handle_keys: Обрабатывает нажатия клавиш пользователем для изменения
        направления движения объекта "Змейка".
    set_randomize_position: Устанавливает новую позицию объекта-продукта на
        игровом поле.
    main: Запускает игру "Змейка".
"""
from random import choice, randint
from typing import Optional, Union

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

# Цвета фона - светло-серый.
BOARD_BACKGROUND_COLOR = (211, 211, 211)

# Цвет яблока - красный.
APPLE_COLOR = (255, 0, 0)

# Цвет неправильного продукта - оранжевый.
WRONG_PRODUCT_COLOR = (255, 165, 0)

# Цвет змейки - зелёный.
SNAKE_COLOR = (0, 255, 0)


# Центральная точка экрана.
CENTER_SCREEN_POINT = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

# Скорость движения змейки.
SPEED = 5

# Настройка игрового окна.
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
screen.fill(BOARD_BACKGROUND_COLOR)
pg.display.flip()

# Заголовок окна игрового поля.
pg.display.set_caption("Змейка")

# Настройка времени.
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов.

    Атрибуты:
        position: Позиция объекта на игровом поле. Инициализируется
            как центральная точка экрана.
        body_color: Цвет объекта. Переопределяется в дочерних классах.
            Инициализируется как None.

    Методы:
        draw: Отрисовывает объект на экране. Переопределяется в дочерних
            классах.
    """

    def __init__(self) -> None:
        """Инициализирует атрибуты класса."""
        self.position: tuple[int, int] = CENTER_SCREEN_POINT
        self.body_color: Optional[tuple[int, int, int]] = None

    def draw(self, surface: pg.Surface) -> None:
        """Отрисовывает объект на экране.

        Параметры:
            surface: Игровое окно.
        """
        pass


class Apple(GameObject):
    """Класс для представления объекта "Яблоко" в игре "Змейка".
    Наследуется от класса GameObject.

    Атрибуты:
        position: Позиция объекта "Яблоко" на игровом поле. Яблоко появляется
            в случайном месте на игровом поле. Инициализируется с помощью
            метода randomize_position.
        body_color: Цвет объекта "Яблоко". Инициализируется RGB-значением
            как красное.

    Методы:
        randomize_position: Устанавливает случайное положение объекта "Яблоко"
            на игровом поле.
        draw: Отрисовывает объект "Яблоко" на игровой поверхности.
    """

    def __init__(self) -> None:
        """Инициализирует объект класса."""
        super().__init__()
        self.body_color: tuple[int, int, int] = APPLE_COLOR
        self.position: tuple[int, int] = self.randomize_position()

    def randomize_position(self) -> tuple[int, int]:
        """Устанавливает случайное положение объекта "Яблоко" на игровом поле.

        Returns:
            Кортеж координат объекта "Яблоко".
        """
        # Обработка краёв экрана достигается применением операции модуля
        # по ширине и высоте экрана (определение остатка от деления).
        random_width = (randint(0, GRID_WIDTH) * GRID_SIZE) % SCREEN_WIDTH
        random_height = (randint(0, GRID_HEIGHT) * GRID_SIZE) % SCREEN_HEIGHT

        return (random_width, random_height)

    def draw(self, surface: pg.Surface) -> None:
        """Отрисовывает объект "Яблоко" на игровой поверхности.

        Параметры:
            surface: Игровое окно.
        """
        rect = pg.Rect(
            (self.position[0], self.position[1]), (GRID_SIZE, GRID_SIZE)
        )
        pg.draw.rect(surface, self.body_color, rect)
        pg.draw.rect(surface, (93, 216, 228), rect, 1)


class WrongProduct(Apple):
    """Класс для представления объекта "Неправильный продукт" в игре "Змейка".
    Наследуется от класса Apple.

    Атрибуты:
        position: Позиция объекта "Неправильный продукт" на игровом поле.
            Неправильный продукт появляется в случайном месте на игровом поле.
            Инициализируется с помощью метода randomize_position.
        body_color: Цвет объекта "Неправильный продукт". Инициализируется
            RGB-значением как оранжевый.

    Методы:
        randomize_position: Устанавливает случайное положение объекта
            "Неправильный продукт" на игровом поле. Наследуется от
            родительского класса Apple.
        draw: Отрисовывает объект "Неправильный продукт" на игровой
            поверхности. Наследуется от родительского класса Apple.
        reset_draw: Затирает объект "Неправильный продукт" на игровой
            поверхности.
    """

    def __init__(self) -> None:
        """Инициализирует объект класса."""
        super().__init__()
        self.body_color: tuple[int, int, int] = WRONG_PRODUCT_COLOR

    def reset_draw(self, surface: pg.Surface) -> None:
        """Затирает объект "Неправильный продукт" на игровой поверхности.

        Параметры:
            surface: Игровое окно.
        """
        wrog_product_rect = pg.Rect(
            (self.position[0], self.position[1]), (GRID_SIZE, GRID_SIZE)
        )
        pg.draw.rect(surface, BOARD_BACKGROUND_COLOR, wrog_product_rect)


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
        next_direction: Следующее направление движения, которое будет применено
            после обработки нажатия клавиши. Определяется внешней функцией
            handle_keys.
        body_color: Цвет объекта "Змейка". Инициализируется RGB-значением как
            зелёная.
        last: Позиция последнего сегмента объекта "Змейка" (последнего элемента
            списка positions). Инициализируется значением None.

    Методы:
        update_direction: Обновляет направление движения объекта "Змейка".
        move: Обновляет позицию объекта "Змейка".
        get_head_position: Возвращает позицию головы (первого элемента списка
            positions) объекта "Змейка".
        reset: Сбрасывает объект "Змейка" в начальное состояние после
            столкновения с собой.
        draw: Отрисовывает объект "Змейка" на игровой поверхности.
    """

    def __init__(self) -> None:
        """Инициализирует объект класса."""
        super().__init__()
        self.length: int = 1
        self.positions: list[tuple[int, int]] = [self.position]
        self.direction: tuple[int, int] = RIGHT
        self.next_direction: Optional[tuple[int, int]] = None
        self.body_color: tuple[int, int, int] = SNAKE_COLOR
        self.last: Optional[tuple[int, int]] = None

    def update_direction(self) -> None:
        """Обновляет направление движения объекта "Змейка"."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Обновляет позицию объекта "Змейка"."""
        # Текущее положение головы.
        current_head_position = self.get_head_position()

        # Определение новой позиции головы.
        # Обработка краёв экрана достигается применением операции модуля
        # по ширине и высоте экрана (определение остатка от деления).
        if self.direction in (UP, DOWN):
            next_head_position = (
                current_head_position[0],
                (
                    (current_head_position[1] + self.direction[1] * GRID_SIZE)
                    % SCREEN_HEIGHT
                ),
            )
        elif self.direction in (RIGHT, LEFT):
            next_head_position = (
                (
                    (current_head_position[0] + self.direction[0] * GRID_SIZE)
                    % SCREEN_WIDTH
                ),
                current_head_position[1],
            )

        # Проверка на столкновение с собой.
        if next_head_position in self.positions:
            self.reset()

        # Обновление списка позиций.
        else:
            self.positions.insert(0, next_head_position)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self, surface: pg.Surface) -> None:
        """Отрисовывает объект "Змейка" на игровой поверхности с затиранием
        следа.

        Параметры:
            surface: Игровое окно.
        """
        for position in self.positions[:-1]:
            rect = pg.Rect(
                (position[0], position[1]), (GRID_SIZE, GRID_SIZE)
            )
            pg.draw.rect(surface, self.body_color, rect)
            pg.draw.rect(surface, (93, 216, 228), rect, 1)

        # Отрисовка головы змейки.
        head = self.positions[0]
        head_rect = pg.Rect((head[0], head[1]), (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(surface, self.body_color, head_rect)
        pg.draw.rect(surface, (93, 216, 228), head_rect, 1)

        # Затирание последнего сегмента.
        if self.last:
            last_rect = pg.Rect(
                (self.last[0], self.last[1]), (GRID_SIZE, GRID_SIZE)
            )
            pg.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает позицию головы объекта "Змейка".

        Параметры:
            positions: Список, содержащий позиции всех сегментов тела объекта
                "Змейка".

        Returns:
            Кортеж с координатами текущей позиции головы объекта "Змейка"
        """
        return self.positions[0]

    def reset(self) -> None:
        """Сбрасывает объект "Змейка" в начальное состояние после столкновения
        с собой.
        """
        # Сброс длины змейки.
        self.length = 1

        # Сброс позиций змейки.
        self.position = CENTER_SCREEN_POINT
        self.positions = [self.position]

        # Изменение направления движения змейки.
        directions = (UP, DOWN, RIGHT, LEFT)
        self.direction = choice(directions)

        # Очистка экрана.
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(game_object: Snake) -> None:
    """Обрабатывает нажатия клавиш пользователем для изменения направления
    движения объекта "Змейка".

    Параметры:
        game_object: Объект класса Snake.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP

            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN

            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT

            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def set_randomize_position(game_product: Union[Apple, WrongProduct],
                           game_object: Snake) -> None:
    """Установка новой позиции объекта-продукта на игровом поле.

    Параметры:
        game_product: объект класса Apple или WrongProduct.
        game_object: объект класса Snake.
    """
    game_product.position = game_product.randomize_position()
    # Уточнение позиции объекта-продукта в случае совпадения новой позиции
    # объекта-продукта с позицией змейки.
    while game_product.position in game_object.positions:
        game_product.position = game_product.randomize_position()


def main():
    """Запускает игру "Змейка"."""
    # Инициализация объектов классов.
    apple = Apple()
    snake = Snake()
    wrong_product = WrongProduct()

    while True:
        # Замедление скорости движения змейки до SPEED раз в секунду.
        clock.tick(SPEED)

        # Обработка нажатий клавиш.
        handle_keys(snake)

        # Обновление направления движения змейки.
        snake.update_direction()

        # Проверка, съедено ли яблоко.
        if snake.get_head_position() == apple.position:
            snake.length += 1

            # Изменение положения яблока на игровом поле.
            set_randomize_position(apple, snake)

            # Затирание неправильного продукта.
            wrong_product.reset_draw(screen)

            # Изменение положения неправильного продукта на игровом поле.
            set_randomize_position(wrong_product, snake)

        # Проверка, съеден ли неправильный продукт.
        elif snake.get_head_position() == wrong_product.position:
            # Сброс змейки в начальное состояние.
            snake.reset()

            # Изменение положения неправильного продукта на игровом поле.
            set_randomize_position(wrong_product, snake)

        # Движение змейки.
        snake.move()

        # Отображение яблока, неправильного продукта и змейки.
        apple.draw(screen)
        wrong_product.draw(screen)
        snake.draw(screen)

        # Обновление дисплея.
        pg.display.update()


if __name__ == "__main__":
    main()
