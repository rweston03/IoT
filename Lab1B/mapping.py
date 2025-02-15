from picarx import Picarx
from time import sleep
import numpy as np
from typing import Iterator
import copy

MAX_ANGLE = 35 # theoretically 90
GRID_SIZE = 100
SLEEP_TIME = 0.1
INCREMENT = 5
px = Picarx()

def get_mu_distance(angle):
    px.set_cam_pan_angle(angle)
    while True:
        readings = []
        i = 0

        # take three readings
        while i < 3:
            distance = round(px.ultrasonic.read(), 2)
            print("distance: ", distance)

            if distance < 0:
                distance = 500

            readings.append(distance)
            sleep(SLEEP_TIME)
            i += 1

        # if readings are very different from each other, repeat readings
        if np.std(readings) < 2:
            return np.mean(readings)

if __name__=='__main__':   
    get_grid()

# Adding code from Red Blob Games source "Implementation of A*" 
# found on https://www.redblobgames.com/pathfinding/a-star/implementation.html#python-astar
GridLocation = tuple[int, int]

class SquareGrid:
    def __init__(self, grid: list[list[int]]):
        self.width = len(grid[0]) 
        self.height = len(grid)
        self.walls: list[GridLocation] = []
        for row_idx, row in enumerate(grid):
            for col_idx, value in enumerate(row):
                if value == 1:
                    coords = (row_idx, col_idx)
                    self.walls.append(coords)     
        self.grid = grid

    def in_bounds(self, id: GridLocation) -> bool:
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, id: GridLocation) -> bool:
        return id not in self.walls

    def neighbors(self, id: GridLocation) -> Iterator[GridLocation]:
        (x, y) = id
        neighbors = [(x+1, y), (x-1, y), (x, y-1), (x, y+1)] # E W N S
        # see "Ugly paths" section for an explanation:
        if (x + y) % 2 == 0: neighbors.reverse() # S N W E
        results = filter(self.in_bounds, neighbors)
        results = filter(self.passable, results)
        return results

    def cost(self, start: GridLocation, end: GridLocation):
        return 1

    def printGrid(self):
        output = ""
        for row_idx, row in enumerate(self.grid):
            for col_idx, value in enumerate(row):
                output = output + str(value) + " "
            output = output + "\n"
        print(output)

    def printPath(self, path):
        gridCopy = copy.deepcopy(self.grid)
        for coord in path:
            x = coord[0]
            y = coord[1]

            gridCopy[x][y] = 2
        output = ""
        for row_idx, row in enumerate(gridCopy):
            for col_idx, value in enumerate(row):
                output = output + str(value) + " "
            output = output + "\n"
        print(output)


def get_grid():
    try: 
            # assume that the entire space is open
            area = np.zeros((GRID_SIZE, GRID_SIZE), dtype = int)

            # starting in the middle bottom of grid
            origin = ((int)(GRID_SIZE/2), 0)

            # angles from -MAX_ANGLE to MAX_ANGLE, incrementing by INCREMENT
            angles = list(range(-MAX_ANGLE, MAX_ANGLE+1, INCREMENT)) 

            for angle in angles:
                mu_distance = get_mu_distance(angle)

                # figure out how far the object is in the x and y directions
                rad_angle = angle * np.pi / 180.
                x = mu_distance*np.sin(rad_angle)
                y = mu_distance*np.cos(rad_angle)

                # if the object is in the grid, mark grid space as 1
                (i, j) = (origin[0] + x, origin[1] + y)
                if i > 0 and i < GRID_SIZE and j > 0 and j < GRID_SIZE:
                    i = round(i)
                    j = round(j)
                    area[i][j] = 1

            grid = SquareGrid(area)            
            return grid

    finally:
        print("finished mapping")
