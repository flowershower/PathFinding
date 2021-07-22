import pygame
import pathfinding
from types import SimpleNamespace


# Класс, реализующий перемещаемую клетку
class MovingDot:
    def __init__(self, pos):
        self.__x = pos[0]
        self.__y = pos[1]

    def get_pos(self):
        return self.__x, self.__y

    def set_pos(self, pos):
        self.__x = pos[0]
        self.__y = pos[1]

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y


# Расширение функционала класса MovingDot
# через наследование
class PlayerDot(MovingDot):
    def __init__(self, pos):
        super().__init__(pos)
        self.__direction = (0, 1)

    def set_direction(self, direct):
        self.__direction = direct

    def get_direction(self):
        return self.__direction


colors = SimpleNamespace(**{'gray': (127, 127, 127), 'black': (0, 0, 0), 'red': (255, 0, 0), 'white': (255, 255, 255),
                            'blue': (0, 0, 255)})

settings = SimpleNamespace(**{'width': 800})
player = PlayerDot((2, 2))
enemy = MovingDot((44, 40))

new_graph = pathfinding.prepare_graph('maze.png')
n = new_graph.get_size()


# функция поиска кратчайшего пути из начальной точки в конечную
def move_enemy(graph_sample, from_loc, to_loc):
    path = graph_sample.star_search(from_loc, to_loc)
    return path[1].get_pos() if path else from_loc


# Главная функция, в которой описан игровой цикл
def main(graph):
    run = True

    while run:
        # Пока приложение запущено,
        # происходит считывание пользвательского ввода
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            directions = {pygame.K_LEFT: (-1, 0), pygame.K_RIGHT: (1, 0), pygame.K_UP: (0, -1), pygame.K_DOWN: (0, 1)}
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pos = tuple(map(sum, zip(player.get_pos(), player.get_direction())))
                    item = graph.get_node(pos)
                    item.reset() if item.is_barrier() else item.make_barrier()
                    # graph.reset_neighbours()
                    graph.update_node_neighbours(pos)
                    enemy.set_pos(move_enemy(graph, enemy.get_pos(), player.get_pos()))
                    redraw_all(graph)

                elif event.key in directions.keys():
                    direction = directions[event.key]
                    player.set_direction(direction)

                    can_move, target, dis = graph.get_node(player.get_pos()).can_get_to(graph.get_graph(), direction)
                    if can_move:
                        player.set_pos(target)
                    enemy.set_pos(move_enemy(graph, enemy.get_pos(), player.get_pos()))
                    redraw_all(graph)

    pygame.quit()


# Отрисовка сетки в окне приложения
def draw_grid(win, rows, wid):
    gap = wid // rows
    for i in range(rows):
        pygame.draw.line(win, colors.gray, (0, i * gap), (wid, i * gap))
        for j in range(rows):
            pygame.draw.line(win, colors.gray, (j * gap, 0), (j * gap, wid))


# Перерисовка всего поля на основе графа
def redraw_all(graph_state):
    game_window.fill(colors.white)
    cell_width = settings.width // n
    for i in range(n):
        # columns
        for j in range(n):
            x_loc = (0 + i) * cell_width
            y_loc = (0 + j) * cell_width
            color = colors.black if graph_state.get_node((i, j)).is_barrier() else colors.white
            pygame.draw.rect(game_window, color, (x_loc, y_loc, cell_width, cell_width))

    pygame.draw.rect(game_window, colors.blue, (player.get_x()*cell_width, player.get_y()*cell_width,
                                                cell_width, cell_width))
    pygame.draw.rect(game_window, colors.red, (enemy.get_x()*cell_width, enemy.get_y()*cell_width,
                                               cell_width, cell_width))

    draw_grid(game_window, n, settings.width)
    pygame.display.update()


# Настройка окна приложения, запуск игрового цикла
game_window = pygame.display.set_mode((settings.width, settings.width))

redraw_all(new_graph)
pygame.display.set_caption("Hide N Seek")

main(new_graph)
