from random import randint

import pygame


# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Частота обработки нажатия клавиш.
FRAMES_PER_SECOND = 60

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш, чтобы
    изменить направление движения змейки.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


# Классы игры
class GameObject:
    """Это базовый класс, от которого наследуются другие игровые объекты.

    Он содержит общие атрибуты игровых объектов — позицию и цвет объекта.
    Содержит абстрактный метод для отрисовки объекта на игровом поле — draw.
    """

    def __init__(self):
        center_x = GRID_WIDTH // 2 * GRID_SIZE
        center_y = GRID_HEIGHT // 2 * GRID_SIZE
        # Позиция объекта на игровом поле
        self.position = (center_x, center_y)
        # Цвет объекта
        self.body_color = None

    def draw(self):
        """Определяет, как объект отрисовывается на экране.

        Абстрактный метод.
        """
        pass


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
            body_color=APPLE_COLOR):
        # Начальная позиция задается в main() методом randomize_position().
        self.position = None
        # Цвет яблока.
        self.body_color = body_color

    def randomize_position(self):
        """Устанавливает случайное положение яблока на игровом поле."""
        new_x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        new_y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (new_x, new_y)

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


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
            body_color=SNAKE_COLOR):
        # Длина змейки.
        self.length = 1
        center_x = GRID_WIDTH // 2 * GRID_SIZE
        center_y = GRID_HEIGHT // 2 * GRID_SIZE
        # Список координат сегментов змейки.
        self.positions = [(center_x, center_y)]
        # Позиция головы змейки.
        self.position = self.positions[0]
        # Направление движения змейки.
        self.direction = RIGHT
        # Следующее направление движения змейки.
        self.next_direction = None
        # Цвет змейки.
        self.body_color = body_color
        # Хвост змейки, который будет затёрт при вызове draw().
        self.last = None

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки: добавляет новую голову."""
        self.update_direction()
        new_position = (
            (self.position[0] + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (self.position[1] + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT)
        self.positions.insert(0, new_position)
        self.position = new_position
        self.length += 1

    def shrink(self):
        """Обновляет позицию змейки: удаляет хвостовой сегмент."""
        if self.length > 0:
            self.last = self.positions.pop()
            self.length -= 1

    def draw(self):
        """Отрисовывает змейку на экране.

        Отрисовывается только голова змейки. Внутренние сегменты
        отрисовываются постепенно при увеличении размера змейки.

        При удалении хвоста змейки из списка координат, он затирается.
        """
        head = self.position
        rect = (pygame.Rect(head, (GRID_SIZE, GRID_SIZE)))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
            self.last = None

    def check_collision(self) -> bool:
        """Проверяет столкновение головы змейки с ячейкой тела."""
        ind = 1
        while ind < self.length:
            if self.position == self.positions[ind]:
                return True
            ind += 1
        return False

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.position

    def reset(self):
        """Сбрасывает змейку в начальное состояние.

        Затирает все ячейки предыдущей змейки.
        """
        for position in self.positions:
            last_rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

        self.__init__()


def main():
    """Основная логика игры.

    Цикл игры разбивается на две части: обработку нажатий (с высокой частотой
    FRAMES_PER_SECOND) и движение змейки (с частотой SPEED).
    """
    # Инициализация PyGame:
    pygame.init()
    # Создание объектов на игровом поле
    apple = Apple()
    snake = Snake()
    apple.randomize_position()

    # Основной цикл игры
    frame = 0
    move_freq = FRAMES_PER_SECOND // SPEED
    while True:
        clock.tick(FRAMES_PER_SECOND)
        frame = (frame + 1) % FRAMES_PER_SECOND

        # Выполняется с частотой FRAMES_PER_SECOND
        handle_keys(snake)

        # Выполняется с частотой SPEED
        if not frame % move_freq:
            snake.move()

            # При движении змейка "вычищает" свой хвост.
            # Если змейка съедает яблоко, то хвост не передвигается.
            # При столкновении змейки сама с собой, игра начинается заново.
            if snake.get_head_position() == apple.position:
                apple.randomize_position()
            elif snake.check_collision():
                snake.reset()
            else:
                snake.shrink()

        snake.draw()
        apple.draw()

        pygame.display.update()


if __name__ == '__main__':
    main()
