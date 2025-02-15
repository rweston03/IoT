# Navigation - can be started after mapping and routing, must be completed last to bring all pieces together
import mapping
import routing
import json
from mapping import get_grid, GRID_SIZE, px
from routing import a_star_search 
from object_detection import start_object_detection, detections
import threading
import time

RESCAN_INTERVAL = 25
def main():
    try:
        threading.Thread(target=start_object_detection).start()
        current_location = (GRID_SIZE - 1, 50)
        destination = (0, 99)
        orientation = "NORTH" # Bot always starts on the bottom middle of the grid facing north

        # loop until reaches destination
        # on each loop, it gets a new grid where it is on the bottom middle of the grid and updates the 
        # coordinates of the destination based on where it moved. it moves RESCAN_INTERVAL steps and then rescans
        while True:
            print(f"scanning...")
            origin = (GRID_SIZE - 1, 50)
            grid = get_grid()
            path = a_star_search(grid, current_location, destination)
            print(f'{path=}')
            grid.printPath(path, destination, current_location)
            steps_to_take = path[0:RESCAN_INTERVAL]
            print(f"{steps_to_take}=")
            if len(steps_to_take) == 0:
                return

            if len(detections) > 0 and detections[0].label == "stop sign":
                print("stop for x seconds")
                
            px.set_dir_servo_angle(0)
            for step in steps_to_take:
                if orientation == "NORTH":
                    if step[0] == current_location[0] - 1:
                        print("north forward")
                    elif step[1] == current_location[1] - 1:
                        print("north to west")
                        orientation = "WEST"
                        px.set_dir_servo_angle(-30)
                    elif step[1] == current_location[1] + 1:
                        print("north to east")
                        orientation = "EAST"
                        px.set_dir_servo_angle(30)
                elif orientation == "EAST":
                    if step[0] == current_location[0] - 1:
                        print("east to north")
                        orientation = "NORTH"
                        px.set_dir_servo_angle(-30)
                    elif step[1] == current_location[1] + 1:
                        print("east forward")
                    elif step[1] == current_location[1] - 1:
                        print("dont think this should happen, would be backwards 1")
                elif orientation == "WEST":
                    if step[0] == current_location[0] - 1:
                        print("west to north")
                        orientation = "NORTH"
                        px.set_dir_servo_angle(30)
                    elif step[1] == current_location[1] + 1:
                        print("dont think this should happen, would be backwards 2")
                    elif step[1] == current_location[1] - 1:
                        print("west forward")
                px.forward(5)
                time.sleep(0.25)
                px.set_dir_servo_angle(0)
                current_location = step
            px.forward(0)

            # Need to reset the orientation so it is always facing north at the end of processing a batch of steps
            print(f'reorienting from {orientation=} to north')
            if orientation == "WEST":
                # Move backwards, turn to the right, then go backwards again to try to end up in a similar spot
                px.backward(5)
                time.sleep(0.5)
                px.set_dir_servo_angle(30)
                px.forward(5)
                time.sleep(0.5)
                px.backward(5)
                time.sleep(0.5)
                px.forward(0)
                # now it should be facing north
            if orientation == "EAST":
                # Move backwards, turn to the left, then go backwards again to try to end up in a similar spot
                px.backward(5)
                time.sleep(0.5)
                px.set_dir_servo_angle(30)
                px.forward(5)
                time.sleep(0.5)
                px.backward(5)
                time.sleep(0.5)
                px.forward(0)
                #now it should be facing north

            # we can't really know for sure, but we'll assume that the navigation so far has taken us to the position of the last step
            last_step = steps_to_take[-1]

            #now, since we're going to re scan the grid which means the bot will be at the bottom again, we need to update the destination
            #to be in the new spot based on the last step in the path

            # bot starts at 99, 50
            # bot moves to x, y
            # destination was 0,99
            # new destination is ?
            print(f'bot moved from {origin=} to {last_step=}')
            delta_x = last_step[0] - origin[0]
            delta_y = last_step[1] - origin[1]

            # Update the destination based on the bot's last position
            old_destination = destination 
            destination = (destination[0] - delta_x, destination[1] - delta_y)
            print(f'{old_destination=}, {destination=}')

            current_location = origin 
            time.sleep(5)
    finally:
        px.forward(0)

        

        # object = detections[0]

        # if object == "Stop Sign":
        #     time.sleep(0.5)
        #     px.forward(POWER)

if __name__ == "__main__":
    main()