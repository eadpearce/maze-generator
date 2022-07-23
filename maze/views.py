from django.views.generic import FormView
from maze.forms import MazeForm
import random

# Maze code adapted from https://github.com/OrWestSide/python-scripts/blob/master/maze.py


class Cell:
    class_name = "cell"


class Wall:
    class_name = "wall"


class Unvisited:
    class_name = "unvisited"


class Index(FormView):
    template_name = "maze/index.html"
    form_class = MazeForm
    success_url = "/"

    # Find number of surrounding cells
    def surrounding_cells(self, maze, rand_wall):
        s_cells = 0
        if isinstance(maze[rand_wall[0]-1][rand_wall[1]], Cell):
            s_cells += 1
        if isinstance(maze[rand_wall[0]+1][rand_wall[1]], Cell):
            s_cells += 1
        if isinstance(maze[rand_wall[0]][rand_wall[1] - 1], Cell):
            s_cells += 1
        if isinstance(maze[rand_wall[0]][rand_wall[1] + 1], Cell):
            s_cells += 1

        return s_cells

    def create_maze(self, width=10, height=10):
        maze = []
        # Denote all cells as unvisited
        for i in range(0, height):
            maze.append([Unvisited() for i in range(0, width)])

        # Randomize starting point and set it a cell
        starting_height = int(random.random()*height)
        starting_width = int(random.random()*width)
        if starting_height == 0:
            starting_height += 1
        if starting_height == height-1:
            starting_height -= 1
        if starting_width == 0:
            starting_width += 1
        if starting_width == width-1:
            starting_width -= 1

        # Mark it as a cell and add surrounding walls to the list
        maze[starting_height][starting_width] = Cell()
        walls = []
        walls.append([starting_height - 1, starting_width])
        walls.append([starting_height, starting_width - 1])
        walls.append([starting_height, starting_width + 1])
        walls.append([starting_height + 1, starting_width])

        # Denote walls in maze
        maze[starting_height - 1][starting_width] = Wall()
        maze[starting_height][starting_width - 1] = Wall()
        maze[starting_height][starting_width + 1] = Wall()
        maze[starting_height + 1][starting_width] = Wall()

        while (walls):
            # Pick a random wall
            rand_wall = walls[int(random.random() * len(walls)) - 1]

            # Check if it is a left wall
            if (rand_wall[1] != 0):
                if (
                    isinstance(maze[rand_wall[0]][rand_wall[1]-1], Unvisited) and
                    isinstance(maze[rand_wall[0]][rand_wall[1]+1], Cell)
                ):
                    # Find the number of surrounding cells
                    s_cells = self.surrounding_cells(maze, rand_wall)

                    if (s_cells < 2):
                        # Denote the new path
                        maze[rand_wall[0]][rand_wall[1]] = Cell()

                        # Mark the new walls
                        # Upper cell
                        if (rand_wall[0] != 0):
                            if not isinstance(maze[rand_wall[0]-1][rand_wall[1]], Cell):
                                maze[rand_wall[0]-1][rand_wall[1]] = Wall()
                            if ([rand_wall[0]-1, rand_wall[1]] not in walls):
                                walls.append([rand_wall[0]-1, rand_wall[1]])

                        # Bottom cell
                        if (rand_wall[0] != height-1):
                            if not isinstance(maze[rand_wall[0]+1][rand_wall[1]], Cell):
                                maze[rand_wall[0]+1][rand_wall[1]] = Wall()
                            if ([rand_wall[0]+1, rand_wall[1]] not in walls):
                                walls.append([rand_wall[0]+1, rand_wall[1]])

                        # Leftmost cell
                        if (rand_wall[1] != 0):
                            if not isinstance(maze[rand_wall[0]][rand_wall[1]-1], Cell):
                                maze[rand_wall[0]][rand_wall[1]-1] = Wall()
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
                    isinstance(maze[rand_wall[0]-1][rand_wall[1]], Unvisited) and
                    isinstance(maze[rand_wall[0]+1][rand_wall[1]], Cell)
                ):

                    s_cells = self.surrounding_cells(maze, rand_wall)
                    if (s_cells < 2):
                        # Denote the new path
                        maze[rand_wall[0]][rand_wall[1]] = Cell()

                        # Mark the new walls
                        # Upper cell
                        if (rand_wall[0] != 0):
                            if not isinstance(maze[rand_wall[0]-1][rand_wall[1]], Cell):
                                maze[rand_wall[0]-1][rand_wall[1]] = Wall()
                            if ([rand_wall[0]-1, rand_wall[1]] not in walls):
                                walls.append([rand_wall[0]-1, rand_wall[1]])

                        # Leftmost cell
                        if (rand_wall[1] != 0):
                            if not isinstance(maze[rand_wall[0]][rand_wall[1]-1], Cell):
                                maze[rand_wall[0]][rand_wall[1]-1] = Wall()
                            if ([rand_wall[0], rand_wall[1]-1] not in walls):
                                walls.append([rand_wall[0], rand_wall[1]-1])

                        # Rightmost cell
                        if (rand_wall[1] != width-1):
                            if not isinstance(maze[rand_wall[0]][rand_wall[1]+1], Cell):
                                maze[rand_wall[0]][rand_wall[1]+1] = Wall()
                            if ([rand_wall[0], rand_wall[1]+1] not in walls):
                                walls.append([rand_wall[0], rand_wall[1]+1])

                    # Delete wall
                    for wall in walls:
                        if (wall[0] == rand_wall[0] and wall[1] == rand_wall[1]):
                            walls.remove(wall)

                    continue

            # Check the bottom wall
            if (rand_wall[0] != height-1):
                if (
                    isinstance(maze[rand_wall[0]+1][rand_wall[1]], Unvisited) and
                    isinstance(maze[rand_wall[0]-1][rand_wall[1]], Cell)
                ):

                    s_cells = self.surrounding_cells(maze, rand_wall)
                    if (s_cells < 2):
                        # Denote the new path
                        maze[rand_wall[0]][rand_wall[1]] = Cell()

                        # Mark the new walls
                        if (rand_wall[0] != height-1):
                            if not isinstance(maze[rand_wall[0]+1][rand_wall[1]], Cell):
                                maze[rand_wall[0]+1][rand_wall[1]] = Wall()
                            if ([rand_wall[0]+1, rand_wall[1]] not in walls):
                                walls.append([rand_wall[0]+1, rand_wall[1]])
                        if (rand_wall[1] != 0):
                            if not isinstance(maze[rand_wall[0]][rand_wall[1]-1], Cell):
                                maze[rand_wall[0]][rand_wall[1]-1] = Wall()
                            if ([rand_wall[0], rand_wall[1]-1] not in walls):
                                walls.append([rand_wall[0], rand_wall[1]-1])
                        if (rand_wall[1] != width-1):
                            if not isinstance(maze[rand_wall[0]][rand_wall[1]+1], Cell):
                                maze[rand_wall[0]][rand_wall[1]+1] = Wall()
                            if ([rand_wall[0], rand_wall[1]+1] not in walls):
                                walls.append([rand_wall[0], rand_wall[1]+1])

                    # Delete wall
                    for wall in walls:
                        if (wall[0] == rand_wall[0] and wall[1] == rand_wall[1]):
                            walls.remove(wall)

                    continue

            # Check the right wall
            if (rand_wall[1] != width-1):
                if (
                    isinstance(maze[rand_wall[0]][rand_wall[1]+1], Unvisited) and
                    isinstance(maze[rand_wall[0]][rand_wall[1]-1], Cell)
                ):

                    s_cells = self.surrounding_cells(maze, rand_wall)
                    if (s_cells < 2):
                        # Denote the new path
                        maze[rand_wall[0]][rand_wall[1]] = Cell()

                        # Mark the new walls
                        if (rand_wall[1] != width-1):
                            if not isinstance(maze[rand_wall[0]][rand_wall[1]+1], Cell):
                                maze[rand_wall[0]][rand_wall[1]+1] = Wall()
                            if ([rand_wall[0], rand_wall[1]+1] not in walls):
                                walls.append([rand_wall[0], rand_wall[1]+1])
                        if (rand_wall[0] != height-1):
                            if not isinstance(maze[rand_wall[0]+1][rand_wall[1]], Cell):
                                maze[rand_wall[0]+1][rand_wall[1]] = Wall()
                            if ([rand_wall[0]+1, rand_wall[1]] not in walls):
                                walls.append([rand_wall[0]+1, rand_wall[1]])
                        if (rand_wall[0] != 0):
                            if not isinstance(maze[rand_wall[0]-1][rand_wall[1]], Cell):
                                maze[rand_wall[0]-1][rand_wall[1]] = Wall()
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
        for i in range(0, height):
            for j in range(0, width):
                if isinstance(maze[i][j], Unvisited):
                    maze[i][j] = Wall()

        # Set entrance and exit
        for i in range(0, width):
            if isinstance(maze[1][i], Cell):
                maze[0][i] = Cell()
                break

        for i in range(width-1, 0, -1):
            if isinstance(maze[height-2][i], Cell):
                maze[height-1][i] = Cell()
                break

        return maze

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        width = int(self.request.GET.get("width", 10))
        height = int(self.request.GET.get("height", 10))
        context["maze"] = self.create_maze(width=width, height=height)
        return context

    def get_initial(self):
        return {
            "width": int(self.request.GET.get("width", 10)),
            "height": int(self.request.GET.get("height", 10))
        }