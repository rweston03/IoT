from picarx import Picarx
from time import sleep
import numpy as np
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
            elif area[i, j] == 0.5:
                map_image[i, j] = [100, 0, 150]
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
            add_padding(area, x1, y1)
            if x1 == x2 and y1 == y2:
                break
            
            e2 = 2*e

            if e2 > -dy:
                e -= dy
                x1 += sx

            if e2 < dx:
                e += dx
                y1 += sy

def add_padding(area, x, y):
    if (x - 1 >= 0) and (area[y][x-1] == 0):
        area[y][x-1] = 0.5

    if (x + 1 < GRID_SIZE) and (area[y][x+1] == 0):
        area[y][x+1] = 0.5

    if (y - 1 >= 0) and (area[y-1][x] == 0):
        area[y-1][x] = 0.5

    if (y + 1 < GRID_SIZE) and (area[y+1][x] == 0):
        area[y+1][x] = 0.5

def get_mu_distance(angle):
    px.set_cam_pan_angle(angle)
    print("ANGLE: ", angle)
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
    try:  
        # assume that the entire space is open
        area = np.zeros((GRID_SIZE, GRID_SIZE))

        # starting in the middle bottom of grid
        origin = ((int)(GRID_SIZE/2), 0)

        # angles from -MAX_ANGLE to MAX_ANGLE, incrementing by INCREMENT
        angles = list(range(-MAX_ANGLE, MAX_ANGLE+1, INCREMENT)) 
        prev = (-1, -1)

        for angle in angles:
            mu_distance = get_mu_distance(angle)
            print("MEAN DISTANCE: ", mu_distance)
            sleep(0.1)

            # figure out how far the object is in the x and y directions
            rad_angle = angle * np.pi / 180.
            x = (int)(mu_distance*np.sin(rad_angle))
            y = (int)(mu_distance*np.cos(rad_angle))


            # if the object is in the grid, mark grid space as 1
            (i, j) = (origin[0] + x, origin[1] + y)

            (x_coord, y_coord) = (i, GRID_SIZE - j - 1)

            if x_coord > 0 and x_coord < GRID_SIZE and y_coord > 0 and y_coord < GRID_SIZE:
                area[y_coord][x_coord] = 1
                add_padding(area, x_coord, y_coord)
                if (prev[0] != -1):
                    mark_line(area, prev, (x_coord, y_coord))
                prev = (x_coord, y_coord)


    finally:
        print("finished mapping")
        print_map(origin, area)
