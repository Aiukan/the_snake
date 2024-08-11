from random import choice, randint

import pygame as pg


# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центр поля.
CENTER_X = GRID_WIDTH // 2 * GRID_SIZE
CENTER_Y = GRID_HEIGHT // 2 * GRID_SIZE
CENTER_POSITION = (CENTER_X, CENTER_Y)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Ширина границы ячейки.
BORDER_WIDTH = 1

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш, чтобы
    изменить направление движения змейки.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit
            elif event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


# Классы игры
class GameObject:
    """Это базовый класс, от которого наследуются другие игровые объекты.

    Он содержит общие атрибуты игровых объектов — позицию и цвета объекта.
    Содержит абстрактный метод для отрисовки объекта на игровом поле — draw.
    """

    def __init__(
            self,
            body_color=None,
            border_color=BORDER_COLOR,
            border_width=BORDER_WIDTH):
        # Цвет объекта
        self.body_color = body_color
        # Цвет границы объекта.
        self.border_color = border_color
        # Ширина границы объекта.
        self.border_width = border_width
        # Позиция объекта на игровом поле
        self.position = CENTER_POSITION

    def draw(self):
        """Определяет, как объект отрисовывается на экране.

        Абстрактный метод.
        """
        raise NotImplementedError(
            'Метод draw() класса {self.__class__.__name__} '
            'не имеет реализации.')


class Apple(GameObject):
    """Это класс, унаследованный от GameObject, описывающий яблоко
    и его поведение.

    Яблоко представляется квадратом размером в одну ячейку игрового поля.

    При создании яблока координаты для него определяются случайным образом
    и сохраняются до тех пор, пока змейка не «съест» яблоко. После этого
    для яблока вновь задаются случайные координаты.
    """

    def __init__(
            self,
            body_color=APPLE_COLOR,
            border_color=BORDER_COLOR,
            border_width=BORDER_WIDTH):
        super().__init__(body_color, border_color, border_width)
        # Переводит положение яблока из центра в случайную незанятую ячейку.
        self.randomize_position()

    def randomize_position(self, occupied=[CENTER_POSITION]):
        """Устанавливает случайное положение яблока на игровом поле.

        Если выбранное положение попадает в набор занятых ячеек occupied,
        то выбирается новое случайное положение.
        """
        while self.position in occupied:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE)

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, self.border_color, rect, self.border_width)


class Snake(GameObject):
    """Это класс, унаследованный от GameObject, описывающий змейку
    и её поведение.

    Змейка — это список координат, каждый элемент списка
    соответствует отдельному сегменту тела змейки. Атрибуты и методы
    класса обеспечивают логику движения, отрисовку, обработку событий
    (нажата клавиша) и другие аспекты поведения змейки в игре.

    Змейка изначально состоит из одной головы — ячейки на игровом
    поле. При запуске игры змейка сразу же начинает движение вправо по
    игровому полю.
    """

    def __init__(
            self,
            body_color=SNAKE_COLOR,
            border_color=BORDER_COLOR,
            border_width=BORDER_WIDTH):
        super().__init__(body_color, border_color, border_width)
        # Длина змейки.
        self.length = 1
        # Список координат сегментов змейки.
        self.positions = [self.position]
        # Направление движения змейки.
        self.direction = RIGHT
        # Следующее направление движения змейки.
        self.next_direction = None
        # Цвет змейки.
        self.body_color = body_color

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет массив позиций змейки.

        Если змейка не съела яблоко на прошлой итерации, то хвост сдвигается.
        """
        # Удаление лишнего элемента
        if len(self.positions) > self.length:
            self.positions.pop()
        x_position, y_position = self.get_head_position()
        x_direction, y_direction = self.direction
        new_position = (
            (x_position + x_direction * GRID_SIZE) % SCREEN_WIDTH,
            (y_position + y_direction * GRID_SIZE) % SCREEN_HEIGHT)
        self.positions.insert(0, new_position)

    def draw(self):
        """Отрисовывает змейку на экране.

        Отрисовывается только голова змейки. Внутренние сегменты
        отрисовываются постепенно при увеличении размера змейки.

        Если змейка не съела яблоко, то её хвост затирается.
        """
        rect = pg.Rect(self.get_head_position(), (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, self.border_color, rect, self.border_width)

        # Затирание лишнего элемента
        if len(self.positions) > self.length:
            last_rect = pg.Rect(self.positions[-1], (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice(DIRECTIONS)
        self.next_direction = None


def main():
    """Основная логика игры.

    Движение змейки осуществляется с частотой SPEED.
    """
    # Инициализация PyGame:
    pg.init()
    # Создание объектов на игровом поле
    apple = Apple()
    snake = Snake()

    # Основной цикл игры
    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Если змейка съедает яблоко, то хвост не передвигается.
        # При столкновении змейки сама с собой, игра начинается заново.
        # Иначе хвост является лишним и будет затёрт.
        if snake.get_head_position() == apple.position:
            apple.randomize_position(snake.positions)
            snake.length += 1
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            # Позиция яблока меняется только если оно находилось в центре.
            apple.randomize_position()
            screen.fill(BOARD_BACKGROUND_COLOR)

        snake.draw()
        apple.draw()

        pg.display.update()


if __name__ == '__main__':
    main()
