from queue import PriorityQueue
from reader import get_grid_from_img, get_grid_from_json


# Эвристическая функция H
# расчёт Евклидова расстояния
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


# Класс, реализующий вершину графа
class Node:
    def __init__(self, row, col, total_rows):
        self.__row = row
        self.__col = col
        self.__total_rows = total_rows

        self.__neighbours = []
        self.__type = None

    def get_pos(self):
        return self.__row, self.__col

    def get_neighbours(self):
        return self.__neighbours

    def get_state(self, state):
        return self.__type == state

    def is_closed(self):
        return self.get_state('closed')

    def is_open(self):
        return self.get_state('open')

    def is_barrier(self):
        return self.get_state('barrier')

    def reset(self):
        self.__type = None

    def make_closed(self):
        self.__type = 'closed'

    def make_open(self):
        self.__type = 'open'

    def make_barrier(self):
        self.__type = 'barrier'

    # функция отвечает за проверку:
    # можно ли из данной вершины попасть в
    # соседнюю, расположенную в определённом направлении
    def can_get_to(self, grid, direction):
        (y, x) = direction
        target = (self.__row + y, self.__col + x)

        if max(target) <= self.__total_rows - 1 and min(target) >= 0 \
                and not grid[target[0]][target[1]].is_barrier():
            distance = h((self.__row, self.__col), target)
            if distance <= 1 or (not grid[self.__row + y][self.__col].is_barrier()
                                 and not grid[self.__row][self.__col + x].is_barrier()):
                return True, target, distance
        return False, target, None

    # функция обновления списка смежности для вершины
    # проверяется возможность попасть из текущей вершины в соседние
    def update_neighbours(self, grid):
        self.__neighbours = []
        base_direction_vectors = [(0, 1), (0, -1), (1, 0), (-1, 0),
                                  (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for (y, x) in base_direction_vectors:
            can_get, target, distance = self.can_get_to(grid, (y, x))
            if can_get:
                self.__neighbours.append((grid[target[0]][target[1]], distance))

    def __lt__(self, other):
        return False

    def __repr__(self):
        return f'Square with (x:{self.__row}, y:{self.__col})'


# Класс, реализующий граф
class Graph:
    # Формирование двумерного массива
    # экземпляров класса Node
    def __init__(self, array2d):
        length = len(array2d)
        self.__graph = []
        for i in range(length):
            self.__graph.append([])
            for j in range(length):
                square = Node(i, j, length)
                square.make_barrier() if array2d[i][j] == 0 else square.reset()
                self.__graph[i].append(square)

    def get_graph(self):
        return self.__graph

    def get_node(self, loc):
        return self.__graph[loc[0]][loc[1]]

    def get_size(self):
        return len(self.__graph)

    # Пересчитать список смежности для всех вершин
    def reset_neighbours(self):
        for row in self.__graph:
            for square in row:
                square.update_neighbours(self.__graph)

    # Пересчитать список смежности для соседних вершин
    # при изменении определённой вершины
    def update_node_neighbours(self, node_loc):
        node = self.get_node(node_loc)
        for neighbour in node.get_neighbours():
            neighbour[0].update_neighbours(self.__graph)
        node.update_neighbours(self.__graph)

    # Алгоритм поиска А* для поиска кратчайшего пути
    def star_search(self, start_loc, end_loc):
        start_node = self.get_node(start_loc)
        end_node = self.get_node(end_loc)
        count = 0
        open_set = PriorityQueue()
        open_set.put((0, count, start_node))
        came_from = {}

        g_score = {square: float("inf") for row in self.__graph for square in row}
        g_score[start_node] = 0

        f_score = {square: float("inf") for row in self.__graph for square in row}
        f_score[start_node] = h(start_node.get_pos(), end_node.get_pos())

        open_set_hash = {start_node}

        while not open_set.empty():
            current = open_set.get()[2]
            open_set_hash.remove(current)

            if current == end_node:
                backward = []
                while current in came_from:
                    current = came_from[current]
                    backward.append(current)
                backward.reverse()
                return backward

            for neighbor_object in current.get_neighbours():
                neighbor = neighbor_object[0]
                temp_g_score = g_score[current] + neighbor_object[1]

                if temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end_node.get_pos())
                    if neighbor not in open_set_hash:
                        count += 1
                        open_set.put((f_score[neighbor], count, neighbor))
                        open_set_hash.add(neighbor)
                        neighbor.make_open()

            if current != start_node:
                current.make_closed()
        return False

    def __repr__(self):
        return self.__graph


# Функция подготовки графа путём чтения из файла
def prepare_graph(path):
    extension = path.split('.')[-1]
    if extension.lower() == 'json':
        grid = get_grid_from_json(path)
    else:
        grid = get_grid_from_img(path)
    graph = Graph(grid)
    graph.reset_neighbours()
    return graph

