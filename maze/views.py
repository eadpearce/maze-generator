from django.views.generic import FormView
from maze.forms import MazeForm
import random

# Maze code adapted from https://github.com/OrWestSide/python-scripts/blob/master/maze.py


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


class Unvisited:
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
    def surrounding_cells(self, coords):
        s_cells = 0
        if coords[0] > 0 and coords[0] < self.width-1 and coords[1] > 0 and coords[1] < self.height-1:
            # top
            if isinstance(self.maze[coords[0]-1][coords[1]], Cell):
                s_cells += 1
            # bottom
            if isinstance(self.maze[coords[0]+1][coords[1]], Cell):
                s_cells += 1
            # left
            if isinstance(self.maze[coords[0]][coords[1] - 1], Cell):
                s_cells += 1
            # rght
            if isinstance(self.maze[coords[0]][coords[1] + 1], Cell):
                s_cells += 1

        return s_cells

    def create_maze(self):
        self.maze = []
        # Denote all cells as unvisited
        for i in range(0, self.height):
            self.maze.append([Unvisited() for i in range(0, self.width)])

        # Randomize starting point and set it a cell
        starting_height = int(random.random()*self.height)
        starting_width = int(random.random()*self.width)
        if starting_height == 0:
            starting_height += 1
        if starting_height == self.height-1:
            starting_height -= 1
        if starting_width == 0:
            starting_width += 1
        if starting_width == self.width-1:
            starting_width -= 1

        # Mark it as a cell and add surrounding walls to the list
        self.maze[starting_height][starting_width] = Cell(starting_width, starting_height)
        walls = []
        walls.append([starting_height - 1, starting_width])
        walls.append([starting_height, starting_width - 1])
        walls.append([starting_height, starting_width + 1])
        walls.append([starting_height + 1, starting_width])

        # Denote walls in maze
        self.maze[starting_height - 1][starting_width] = Wall(starting_width, starting_height - 1)
        self.maze[starting_height][starting_width - 1] = Wall(starting_width - 1, starting_height)
        self.maze[starting_height][starting_width + 1] = Wall(starting_width + 1, starting_height)
        self.maze[starting_height + 1][starting_width] = Wall(starting_width, starting_height + 1)

        while (walls):
            # Pick a random wall
            rand_wall = walls[int(random.random() * len(walls)) - 1]

            # Check if it is a left wall
            if (rand_wall[1] != 0):
                if (
                    isinstance(self.maze[rand_wall[0]][rand_wall[1]-1], Unvisited) and
                    isinstance(self.maze[rand_wall[0]][rand_wall[1]+1], Cell)
                ):
                    # Find the number of surrounding cells
                    s_cells = self.surrounding_cells(rand_wall)

                    if (s_cells < 2):
                        # Denote the new path
                        self.maze[rand_wall[0]][rand_wall[1]] = Cell(rand_wall[1], rand_wall[0])

                        # Mark the new walls
                        # Upper cell
                        if (rand_wall[0] != 0):
                            if not isinstance(self.maze[rand_wall[0]-1][rand_wall[1]], Cell):
                                self.maze[rand_wall[0]-1][rand_wall[1]] = Wall(rand_wall[1], rand_wall[0]-1)
                            if ([rand_wall[0]-1, rand_wall[1]] not in walls):
                                walls.append([rand_wall[0]-1, rand_wall[1]])

                        # Bottom cell
                        if (rand_wall[0] != self.height-1):
                            if not isinstance(self.maze[rand_wall[0]+1][rand_wall[1]], Cell):
                                self.maze[rand_wall[0]+1][rand_wall[1]] = Wall(rand_wall[1], rand_wall[0]+1)
                            if ([rand_wall[0]+1, rand_wall[1]] not in walls):
                                walls.append([rand_wall[0]+1, rand_wall[1]])

                        # Leftmost cell
                        if (rand_wall[1] != 0):
                            if not isinstance(self.maze[rand_wall[0]][rand_wall[1]-1], Cell):
                                self.maze[rand_wall[0]][rand_wall[1]-1] = Wall(rand_wall[1]-1, rand_wall[0])
                            if ([rand_wall[0], rand_wall[1]-1] not in walls):
                                walls.append([rand_wall[0], rand_wall[1]-1])

                    # Delete wall
                    for wall in walls:
                        if (wall[0] == rand_wall[0] and wall[1] == rand_wall[1]):
                            walls.remove(wall)

                    continue

            # Check if it is an upper wall
            if (rand_wall[0] != 0):
                if (
                    isinstance(self.maze[rand_wall[0]-1][rand_wall[1]], Unvisited) and
                    isinstance(self.maze[rand_wall[0]+1][rand_wall[1]], Cell)
                ):

                    s_cells = self.surrounding_cells(rand_wall)
                    if (s_cells < 2):
                        # Denote the new path
                        self.maze[rand_wall[0]][rand_wall[1]] = Cell(rand_wall[1], rand_wall[0])

                        # Mark the new walls
                        # Upper cell
                        if (rand_wall[0] != 0):
                            if not isinstance(self.maze[rand_wall[0]-1][rand_wall[1]], Cell):
                                self.maze[rand_wall[0]-1][rand_wall[1]] = Wall(rand_wall[1], rand_wall[0]-1)
                            if ([rand_wall[0]-1, rand_wall[1]] not in walls):
                                walls.append([rand_wall[0]-1, rand_wall[1]])

                        # Leftmost cell
                        if (rand_wall[1] != 0):
                            if not isinstance(self.maze[rand_wall[0]][rand_wall[1]-1], Cell):
                                self.maze[rand_wall[0]][rand_wall[1]-1] = Wall(rand_wall[1]-1, rand_wall[0])
                            if ([rand_wall[0], rand_wall[1]-1] not in walls):
                                walls.append([rand_wall[0], rand_wall[1]-1])

                        # Rightmost cell
                        if (rand_wall[1] != self.width-1):
                            if not isinstance(self.maze[rand_wall[0]][rand_wall[1]+1], Cell):
                                self.maze[rand_wall[0]][rand_wall[1]+1] = Wall(rand_wall[1]+1, rand_wall[0])
                            if ([rand_wall[0], rand_wall[1]+1] not in walls):
                                walls.append([rand_wall[0], rand_wall[1]+1])

                    # Delete wall
                    for wall in walls:
                        if (wall[0] == rand_wall[0] and wall[1] == rand_wall[1]):
                            walls.remove(wall)

                    continue

            # Check the bottom wall
            if (rand_wall[0] != self.height-1):
                if (
                    isinstance(self.maze[rand_wall[0]+1][rand_wall[1]], Unvisited) and
                    isinstance(self.maze[rand_wall[0]-1][rand_wall[1]], Cell)
                ):

                    s_cells = self.surrounding_cells(rand_wall)
                    if (s_cells < 2):
                        # Denote the new path
                        self.maze[rand_wall[0]][rand_wall[1]] = Cell(rand_wall[1], rand_wall[0])

                        # Mark the new walls
                        if (rand_wall[0] != self.height-1):
                            if not isinstance(self.maze[rand_wall[0]+1][rand_wall[1]], Cell):
                                self.maze[rand_wall[0]+1][rand_wall[1]] = Wall(rand_wall[1], rand_wall[0]+1)
                            if ([rand_wall[0]+1, rand_wall[1]] not in walls):
                                walls.append([rand_wall[0]+1, rand_wall[1]])
                        if (rand_wall[1] != 0):
                            if not isinstance(self.maze[rand_wall[0]][rand_wall[1]-1], Cell):
                                self.maze[rand_wall[0]][rand_wall[1]-1] = Wall(rand_wall[1]-1, rand_wall[0])
                            if ([rand_wall[0], rand_wall[1]-1] not in walls):
                                walls.append([rand_wall[0], rand_wall[1]-1])
                        if (rand_wall[1] != self.width-1):
                            if not isinstance(self.maze[rand_wall[0]][rand_wall[1]+1], Cell):
                                self.maze[rand_wall[0]][rand_wall[1]+1] = Wall(rand_wall[1]+1, rand_wall[0])
                            if ([rand_wall[0], rand_wall[1]+1] not in walls):
                                walls.append([rand_wall[0], rand_wall[1]+1])

                    # Delete wall
                    for wall in walls:
                        if (wall[0] == rand_wall[0] and wall[1] == rand_wall[1]):
                            walls.remove(wall)

                    continue

            # Check the right wall
            if (rand_wall[1] != self.width-1):
                if (
                    isinstance(self.maze[rand_wall[0]][rand_wall[1]+1], Unvisited) and
                    isinstance(self.maze[rand_wall[0]][rand_wall[1]-1], Cell)
                ):

                    s_cells = self.surrounding_cells(rand_wall)
                    if (s_cells < 2):
                        # Denote the new path
                        self.maze[rand_wall[0]][rand_wall[1]] = Cell(rand_wall[1], rand_wall[0])

                        # Mark the new walls
                        if (rand_wall[1] != self.width-1):
                            if not isinstance(self.maze[rand_wall[0]][rand_wall[1]+1], Cell):
                                self.maze[rand_wall[0]][rand_wall[1]+1] = Wall(rand_wall[1]+1, rand_wall[0])
                            if ([rand_wall[0], rand_wall[1]+1] not in walls):
                                walls.append([rand_wall[0], rand_wall[1]+1])
                        if (rand_wall[0] != self.height-1):
                            if not isinstance(self.maze[rand_wall[0]+1][rand_wall[1]], Cell):
                                self.maze[rand_wall[0]+1][rand_wall[1]] = Wall(rand_wall[1], rand_wall[0]+1)
                            if ([rand_wall[0]+1, rand_wall[1]] not in walls):
                                walls.append([rand_wall[0]+1, rand_wall[1]])
                        if (rand_wall[0] != 0):
                            if not isinstance(self.maze[rand_wall[0]-1][rand_wall[1]], Cell):
                                self.maze[rand_wall[0]-1][rand_wall[1]] = Wall(rand_wall[1], rand_wall[0]-1)
                            if ([rand_wall[0]-1, rand_wall[1]] not in walls):
                                walls.append([rand_wall[0]-1, rand_wall[1]])

                    # Delete wall
                    for wall in walls:
                        if (wall[0] == rand_wall[0] and wall[1] == rand_wall[1]):
                            walls.remove(wall)

                    continue

            # Delete the wall from the list anyway
            for wall in walls:
                if (wall[0] == rand_wall[0] and wall[1] == rand_wall[1]):
                    walls.remove(wall)

        # Mark the remaining unvisited cells as walls
        for i in range(0, self.height):
            for j in range(0, self.width):
                if isinstance(self.maze[i][j], Unvisited):
                    self.maze[i][j] = Wall(j, i)

        # Set entrance and exit
        for i in range(0, self.width):
            if isinstance(self.maze[1][i], Cell):
                self.maze[0][i] = Cell(i, 0, entrance=True)
                break

        for i in range(self.width-1, 0, -1):
            if isinstance(self.maze[self.height-2][i], Cell):
                self.maze[self.height-1][i] = Cell(i, self.height - 1, exit=True)
                break

        # Mark the dead ends
        for row in self.maze:
            for coord in row:
                if isinstance(coord, Cell):
                    s_cells = self.surrounding_cells([coord.y, coord.x])
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
