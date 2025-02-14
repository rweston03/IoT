# Navigation - can be started after mapping and routing, must be completed last to bring all pieces together
from picarx import Picarx
import time
import random
from mapping import mapping_function
from routing import a_star_search

# Portions of this code were based off of picar-x examples. Specifically, the avoiding_obstacles.py example
# which was used to gain an understanding of how to program movement of the motor and how to receive input from
# the ultrasonic sensor. The stare_at_you.py picar-x example was used to gain an understanding of how to program
# movement of the camera servos to allow the ultrasonic sensor to scan back and forth.
POWER = 50
SafeDistance = 40   # > 40 safe
DangerDistance = 20 # > 20 && < 40 turn around, 
                    # < 20 backward
MAX_ANGLE = 90 # theoretically 90
GRID_SIZE = 100
MAX_DIFF = 5
SLEEP_TIME = 0.1
INCREMENT = 5

# The maximum rotation of the drive servos is from -30 to 30, so sticking with those two numbers for turning
DirectionList = [-30,30]

def main():
    try:
        px = Picarx()
        px.set_cam_tilt_angle(15)
        distance = 0
        
        graph = mapping_function(px, ((int)(GRID_SIZE/2), 0))
        route = a_star_search(graph, ((int)(GRID_SIZE/2), 0), (80,80), GRID_SIZE)
        if route is not None:
			print("route")
            print(route)
        else:
            print('no route')
        #print(route if route is not None else 'no route')
       
        

    finally:
        print('done')


if __name__ == "__main__":
    main()
