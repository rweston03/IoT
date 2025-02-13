from picarx import Picarx
from time import sleep
import numpy as np

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

            # if reading is negative, ignore reading
            if distance < 0:
                continue

            readings.append[distance]
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

        for angle in angles:
            mu_distance = get_mu_distance(angle)

            # figure out how far the object is in the x and y directions
            rad_angle = angle * np.pi / 180.
            x = mu_distance*np.sin(rad_angle)
            y = mu_distance*np.cos(rad_angle)

            # if the object is in the grid, mark grid space as 1
            (i, j) = origin + (x, y)
            if i > 0 and i < GRID_SIZE and j > 0 and j < GRID_SIZE:
                area[i][j] = 1


    finally:
        print("finished mapping")
