# Navigation - can be started after mapping and routing, must be completed last to bring all pieces together
import mapping
import routing
import json
from mapping import get_grid, GRID_SIZE, px
from routing import a_star_search 
from object_detection import start_object_detection, detections
import threading
import time
def main():
    try:
        threading.Thread(target=start_object_detection).start()
        current_location = ((int)(GRID_SIZE/2), 0)
        destination = (0, 99)
        orientation = "EAST"

        while True:
            # loop until reaches destination; see the 'return' statement
            # on each loop, it gets a new grid and updates the destination based on where it moved
            grid = get_grid()
            path = a_star_search(grid, current_location, destination)
            grid.printPath(path)

            # scanning takes a while, so for each loop, we will try to process 25 steps (max steps to reach destination is 100)
            steps_to_take = path[0:25]
            print(f"{steps_to_take}=")
            if len(steps_to_take) == 0:
                return
                
            px.set_dir_servo_angle(0)
            for step in steps_to_take:
                if orientation == "EAST":
                    if step[1] == current_location[1] + 1:
                        print("forward")
                    elif step[0] == current_location[0] - 1:
                        print("left")
                        orientation = "NORTH"
                        px.set_dir_servo_angle(-30)
                    elif step[0] == current_location[0] + 1:
                        print("right")
                        orientation = "SOUTH"
                        px.set_dir_servo_angle(30)
                elif orientation == "NORTH":
                    if step[1] == current_location[1] + 1:
                        print("right")
                        orientation = "EAST"
                        px.set_dir_servo_angle(30)
                    elif step[0] == current_location[0] - 1:
                        print("forward")
                    elif step[0] == current_location[0] + 1:
                        print("dont think this should happen, would be backwards 1")
                elif orientation == "SOUTH":
                    if step[1] == current_location[1] + 1:
                        print("left")
                        orientation = "EAST"
                        px.set_dir_servo_angle(-30)
                    elif step[0] == current_location[0] - 1:
                        print("dont think this should happen, would be backwards 2")
                    elif step[0] == current_location[0] + 1:
                        print("forward")
                px.forward(5)
                time.sleep(0.25)
                px.set_dir_servo_angle(0)
                current_location = step
            px.forward(0)
            time.sleep(5)
    finally:
        px.forward(0)

        

        # object = detections[0]

        # if object == "Stop Sign":
        #     time.sleep(0.5)
        #     px.forward(POWER)

if __name__ == "__main__":
    main()