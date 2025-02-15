from picarx import Picarx
from time import sleep
import numpy as np
from typing import Iterator
import copy
import cv2

MAX_ANGLE = 90 # theoretically 90
GRID_SIZE = 100
MAX_DIFF = 5
SLEEP_TIME = 0.1
INCREMENT = 5
px = Picarx()

def print_map(origin, area):
    map_image = np.zeros((GRID_SIZE, GRID_SIZE, 3), dtype=np.uint8)
    
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if area[i, j] == 1:
                map_image[i, j] = [0, 0, 255]
            else:
                map_image[i, j] = [0, 255, 0]

    map_image[GRID_SIZE - origin[1] - 1, origin[0]] = [255, 0, 0]
    
    cv2.imwrite("map_image.png", map_image)

def mark_line(area, p1, p2):
    (x1, y1) = p1
    (x2, y2) = p2

    dx = np.abs(x2 - x1)
    dy = np.abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    e = dx - dy

    if dx < MAX_DIFF and dy < MAX_DIFF:
        while True:
            area[y1][x1] = 1
            if x1 == x2 and y1 == y2:
                break
            
            e2 = 2*e

            if e2 > -dy:
                e -= dy
                x1 += sx

            if e2 < dx:
                e += dx
                y1 += sy

def get_mu_distance(angle):
    px.set_cam_pan_angle(angle)
    while True:
        readings = []
        i = 0

        # take three readings
        while i < 3:
            distance = round(px.ultrasonic.read(), 2)
            print("distance: ", distance)

            # if reading is negative, ignore reading
            if distance < 0:
                continue

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

    def printPath(self, path, destination, current_location):
        gridCopy = copy.deepcopy(self.grid)
        for coord in path:
            y = coord[0]
            x = coord[1]
            gridCopy[y][x] = 2
        gridCopy[destination[0]][destination[1]] = 5 # destination marked with 5
        gridCopy[current_location[0]][current_location[1]] = 4 # current location marked with 4
        output = ""
        for row_idx, row in enumerate(gridCopy):
            for col_idx, value in enumerate(row):
                output = output + str(value) + " "
            output = output + "\n"
        print(output)


def get_grid():
    try: 
        # assume that the entire space is open
        area = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

        # starting in the middle bottom of grid
        origin = ((int)(GRID_SIZE/2), 0)

        # angles from -MAX_ANGLE to MAX_ANGLE, incrementing by INCREMENT
        angles = list(range(-MAX_ANGLE, MAX_ANGLE+1, INCREMENT)) 
        prev = (-1, -1)

        for angle in angles:
            mu_distance = get_mu_distance(angle)

            # figure out how far the object is in the x and y directions
            rad_angle = angle * np.pi / 180.
            x = (int)(mu_distance*np.sin(rad_angle))
            y = (int)(mu_distance*np.cos(rad_angle))


            # if the object is in the grid, mark grid space as 1
            (i, j) = (origin[0] + x, origin[1] + y)

            (x_coord, y_coord) = (i, GRID_SIZE - j - 1)

            if x_coord > 0 and x_coord < GRID_SIZE and y_coord > 0 and y_coord < GRID_SIZE:
                area[y_coord][x_coord] = 1
                if (prev[0] != -1):
                    mark_line(area, prev, (x_coord, y_coord))
                prev = (x_coord, y_coord)

        grid = SquareGrid(area)            
        return grid

    finally:
        print("finished mapping")
        print_map(origin, area)
