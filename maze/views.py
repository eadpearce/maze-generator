from django.views.generic import FormView
from maze.forms import MazeForm
import random

# Maze code adapted from https://github.com/OrWestSide/python-scripts/blob/master/maze.py


class Maze:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rows = []

        # Denote all cells as unvisited
        for y in range(0, self.height):
            self.rows.append([Unvisited(x, y) for x in range(0, self.width)])

    def __getitem__(self, item):
        return self.rows[item]

    @property
    def max_x(self):
        return self.width - 1

    @property
    def max_y(self):
        return self.height - 1

    @property
    def all(self):
        return [coord for row in self.rows for coord in row]


class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y


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

    def __str__(self):
        return f"{type(self).__name__} at ({self.x}, {self.y})"


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

    # Find number of surrounding cells
    def surrounding_cells(self, coord):
        s_cells = 0
        s_coords = self.get_surrounding_coords(coord.x, coord.y)
        if coord.y > 0 and coord.y < self.maze.max_y and coord.x > 0 and coord.x < self.maze.max_x:
            for x, y in s_coords:
                if isinstance(self.maze[y][x], Cell):
                    s_cells += 1
        return s_cells

    def create_coordinate(self, cls, x, y, **kwargs):
        self.maze[y][x] = cls(x, y, **kwargs)

    def get_surrounding_coords(self, x, y):
        return [
            [x-1, y],  # left
            [x+1, y],  # right
            [x, y-1],  # top
            [x, y+1],  # bottom
        ]

    def add_wall(self, x, y):
        self.create_coordinate(Wall, x, y)
        self.walls.add(Wall(x, y))

    def mark_top_wall(self, rand_wall):
        # if top is not a cell
        if not isinstance(self.maze[rand_wall.y-1][rand_wall.x], Cell):
            self.add_wall(rand_wall.x, rand_wall.y-1)

    def mark_bottom_wall(self, rand_wall):
        # if bottom is not a cell
        if not isinstance(self.maze[rand_wall.y+1][rand_wall.x], Cell):
            self.add_wall(rand_wall.x, rand_wall.y+1)

    def mark_left_wall(self, rand_wall):
        # if left is not a cell
        if not isinstance(self.maze[rand_wall.y][rand_wall.x-1], Cell):
            self.add_wall(rand_wall.x-1, rand_wall.y)

    def mark_right_wall(self, rand_wall):
        # if right is not a cell
        if not isinstance(self.maze[rand_wall.y][rand_wall.x+1], Cell):
            self.add_wall(rand_wall.x+1, rand_wall.y)

    def create_maze(self):
        self.maze = Maze(self.width, self.height)

        # Randomize starting point and set it a cell
        starting_height = random.randint(1, self.maze.max_y - 1)
        starting_width = random.randint(1, self.maze.max_x - 1)

        # Mark it as a cell and add surrounding walls to the list
        self.create_coordinate(Cell, starting_width, starting_height)
        self.walls = set()

        for x, y in self.get_surrounding_coords(starting_width, starting_height):
            self.walls.add(Wall(x, y))
            # Denote walls in maze
            self.create_coordinate(Wall, x, y)

        while self.walls:
            # Pick a random wall
            rand_wall = random.choice(list(self.walls))

            # NOTE COORD ORDER
            # maze[y][x]

            # Check if it is a left wall
            if (rand_wall.x != 0):
                # if left is unvisited and right is a cell
                if (
                    isinstance(self.maze[rand_wall.y][rand_wall.x-1], Unvisited) and
                    isinstance(self.maze[rand_wall.y][rand_wall.x+1], Cell)
                ):
                    # Find the number of surrounding cells
                    s_cells = self.surrounding_cells(rand_wall)

                    if (s_cells < 2):
                        # Denote the new path
                        self.create_coordinate(Cell, rand_wall.x, rand_wall.y)

                        # Mark the new walls
                        # Upper cell
                        if (rand_wall.y != 0):
                            self.mark_top_wall(rand_wall)

                        # Bottom cell
                        if (rand_wall.y != self.maze.max_y):
                            self.mark_bottom_wall(rand_wall)

                        # Leftmost cell
                        if (rand_wall.x != 0):
                            self.mark_left_wall(rand_wall)

                    # Delete wall
                    self.walls.remove(rand_wall)

                    continue

            # Check if it is an upper wall
            if (rand_wall.y != 0):
                # if top is unvisited and bottom is a cell
                if (
                    isinstance(self.maze[rand_wall.y-1][rand_wall.x], Unvisited) and
                    isinstance(self.maze[rand_wall.y+1][rand_wall.x], Cell)
                ):

                    s_cells = self.surrounding_cells(rand_wall)
                    if (s_cells < 2):
                        # Denote the new path
                        self.maze[rand_wall.y][rand_wall.x] = Cell(rand_wall.x, rand_wall.y)

                        # Mark the new walls
                        # Upper cell
                        if (rand_wall.y != 0):
                            self.mark_top_wall(rand_wall)

                        # Leftmost cell
                        if (rand_wall.x != 0):
                            self.mark_left_wall(rand_wall)

                        # Rightmost cell
                        if (rand_wall.x != self.maze.max_x):
                            self.mark_right_wall(rand_wall)

                    # Delete wall
                    self.walls.remove(rand_wall)

                    continue

            # Check the bottom wall
            if (rand_wall.y != self.maze.max_y):
                # if bottom is unvisited and top is a cell
                if (
                    isinstance(self.maze[rand_wall.y+1][rand_wall.x], Unvisited) and
                    isinstance(self.maze[rand_wall.y-1][rand_wall.x], Cell)
                ):

                    s_cells = self.surrounding_cells(rand_wall)
                    if (s_cells < 2):
                        # Denote the new path
                        self.maze[rand_wall.y][rand_wall.x] = Cell(rand_wall.x, rand_wall.y)

                        # Mark the new walls
                        if (rand_wall.y != self.maze.max_y):
                            self.mark_bottom_wall(rand_wall)

                        if (rand_wall.x != 0):
                            self.mark_left_wall(rand_wall)

                        if (rand_wall.x != self.maze.max_x):
                            self.mark_right_wall(rand_wall)

                    # Delete wall
                    self.walls.remove(rand_wall)

                    continue

            # Check the right wall
            if (rand_wall.x != self.maze.max_x):
                # if right is unvisited and left is a cell
                if (
                    isinstance(self.maze[rand_wall.y][rand_wall.x+1], Unvisited) and
                    isinstance(self.maze[rand_wall.y][rand_wall.x-1], Cell)
                ):

                    s_cells = self.surrounding_cells(rand_wall)
                    if (s_cells < 2):
                        # Denote the new path
                        self.maze[rand_wall.y][rand_wall.x] = Cell(rand_wall.x, rand_wall.y)

                        # Mark the new walls
                        if (rand_wall.x != self.maze.max_x):
                            self.mark_right_wall(rand_wall)

                        if (rand_wall.y != self.maze.max_y):
                            self.mark_bottom_wall(rand_wall)

                        if (rand_wall.y != 0):
                            self.mark_top_wall(rand_wall)

                    # Delete wall
                    self.walls.remove(rand_wall)

                    continue

            # Delete the wall from the list anyway
            self.walls.remove(rand_wall)

        # Mark the remaining unvisited cells as walls
        for coord in self.maze.all:
            if isinstance(coord, Unvisited):
                self.create_coordinate(Wall, coord.x, coord.y)

        # Set entrance and exit
        # TODO: randomise this?
        # Entrance is at the top edge
        for i in range(0, self.maze.width):
            if isinstance(self.maze[1][i], Cell):
                self.create_coordinate(Cell, i, 0, entrance=True)
                break

        # Exit is at the bottom edge
        for i in range(1, self.maze.width):
            if isinstance(self.maze[self.maze.max_y-1][i], Cell):
                self.create_coordinate(Cell, i, self.maze.max_y, exit=True)
                break

        # Mark the dead ends
        for coord in self.maze.all:
            if isinstance(coord, Cell):
                s_cells = self.surrounding_cells(coord)
                if s_cells == 1:
                    coord.dead_end = True

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.create_maze()
        context["maze"] = self.maze
        return context

    def get_initial(self):
        return {
            "width": min(int(self.request.GET.get("width", 10)), 33),
            "height": min(int(self.request.GET.get("height", 10)), 33)
        }
