from django.views.generic import FormView
from maze.forms import MazeForm
import random

# Maze code adapted from https://github.com/OrWestSide/python-scripts/blob/master/maze.py


class Maze:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cols = []

        # Denote all cells as unvisited
        for x in range(0, self.width):
            self.cols.append([Unvisited(x, y) for y in range(0, self.height)])

    def __getitem__(self, item):
        return self.cols[item]

    @property
    def max_x(self):
        return self.width - 1

    @property
    def max_y(self):
        return self.height - 1

    @property
    def all(self):
        return [coord for row in self.rows for coord in row]

    @property
    def rows(self):
        return list(map(list, zip(*self.cols)))


class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"<{type(self).__name__} at ({self.x}, {self.y})>"

    def __sub__(self, other):
        return Coordinate(abs(self.x - other.x), abs(self.y - other.y))

    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y)


class Cell(Coordinate):

    @property
    def class_name(self):
        if self.start_point:
            return "start-point"
        elif self.dead_end:
            return "dead-end"
        elif self.entrance:
            return "entrance"
        elif self.exit:
            return "exit"
        return "cell"

    def __init__(self, x, y, start_point=False, dead_end=False, entrance=False, exit=False):
        super().__init__(x, y)
        self.start_point = start_point
        self.dead_end = dead_end
        self.entrance = entrance
        self.exit = exit


class Wall(Coordinate):
    class_name = "wall"


class Unvisited(Coordinate):
    class_name = "unvisited"


class Index(FormView):
    template_name = "maze/index.html"
    form_class = MazeForm
    success_url = "/"

    @property
    def width(self):
        return min(int(self.request.GET.get("width", 10)), 33)

    @property
    def height(self):
        return min(int(self.request.GET.get("height", 10)), 33)

    def opposite_squares(self, square):
        squares = []
        adjacent_cells = [c for c in self.get_adjacent_squares(square) if isinstance(c, Cell)]

        if adjacent_cells:
            for c in adjacent_cells:
                cell = self.maze[c.x][c.y]
                opposite_forward = square + (cell - square)
                opposite_back = square - (cell - square)

                squares.append(self.maze[opposite_forward.x][opposite_forward.y])
                squares.append(self.maze[opposite_back.x][opposite_back.y])

        return squares

    def is_edge(self, coord):
        return not (coord.x > 0 and coord.x < self.maze.max_x and coord.y > 0 and coord.y < self.maze.max_y)

    def add_to_maze(self, obj, **kwargs):
        self.maze[obj.x][obj.y] = obj

    def get_adjacent_coords(self, x, y):
        all = [
            [x-1, y],  # left
            [x+1, y],  # right
            [x, y-1],  # top
            [x, y+1],  # bottom
        ]
        # exclude edges
        return [
            [x, y] for x, y in all
            if x > 0 and x < self.maze.max_x and
            y > 0 and y < self.maze.max_y
        ]

    def get_adjacent_squares(self, coord):
        coords = self.get_adjacent_coords(coord.x, coord.y)
        return [
            self.maze[x][y] for x, y in coords
        ]

    def get_adjacent_cells(self, coord):
        return [
            c for c in self.get_adjacent_squares(coord) if isinstance(c, Cell)
        ]

    def create_maze(self):
        self.maze = Maze(self.width, self.height)

        # Randomize starting point and set it as a cell
        starting_height = random.randint(1, self.maze.max_y - 1)
        starting_width = random.randint(1, self.maze.max_x - 1)

        # Mark it as a cell and add surrounding walls to the list
        self.add_to_maze(Cell(starting_width, starting_height, start_point=True))
        self.walls = set()

        for x, y in self.get_adjacent_coords(starting_width, starting_height):
            self.walls.add(Wall(x, y))
            self.add_to_maze(Wall(x, y))

        while self.walls:
            # Pick a random wall
            rand_wall = random.choice(list(self.walls))

            adjacent_squares = self.get_adjacent_squares(rand_wall)

            # find the square on the opposite side to the connecting cell
            adjacent_cells = self.get_adjacent_cells(rand_wall)

            if len(adjacent_cells) == 1:
                for o_square in self.opposite_squares(rand_wall):

                    if isinstance(o_square, Unvisited):
                        if not self.is_edge(o_square):
                            new_wall = Wall(o_square.x, o_square.y)
                            self.add_to_maze(new_wall)
                            self.walls.add(new_wall)
                        self.add_to_maze(Cell(rand_wall.x, rand_wall.y))

                        for a_square in adjacent_squares:
                            if isinstance(a_square, Unvisited):
                                new_wall = Wall(a_square.x, a_square.y)
                                self.add_to_maze(new_wall)
                                self.walls.add(new_wall)

            self.walls.remove(rand_wall)

        # Mark the remaining unvisited cells as walls
        for coord in self.maze.all:
            if isinstance(coord, Unvisited):
                self.add_to_maze(Wall(coord.x, coord.y))

        # Set entrance and exit
        # TODO: randomise this?
        # Entrance is at the top edge
        for i in range(0, self.maze.width):
            if isinstance(self.maze[i][1], Cell):
                self.add_to_maze(Cell(i, 0, entrance=True))
                break

        # Exit is at the bottom edge
        for i in range(1, self.maze.width):
            if isinstance(self.maze[i][self.maze.max_y-1], Cell):
                self.add_to_maze(Cell(i, self.maze.max_y, exit=True))
                break

        # Mark the dead ends
        for coord in self.maze.all:
            if isinstance(coord, Cell):
                s_cells = self.get_adjacent_cells(coord)
                if len(s_cells) == 1:
                    coord.dead_end = True

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.create_maze()
        context["maze"] = self.maze.rows
        return context

    def get_initial(self):
        return {
            "width": min(int(self.request.GET.get("width", 10)), 33),
            "height": min(int(self.request.GET.get("height", 10)), 33)
        }
