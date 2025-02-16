# Navigation - can be started after mapping and routing, must be completed last to bring all pieces together
import mapping
import routing
import json
from mapping import get_grid, GRID_SIZE, px
from routing import a_star_search 
from object_detection import start_object_detection, detections
import threading
import time

RESCAN_INTERVAL = 25 # number of steps to process before rescanning
def main():
    try:
        threading.Thread(target=start_object_detection).start()
        current_location = (GRID_SIZE - 1, 50) # bottom middle of grid
        destination = (0, GRID_SIZE - 1) #Top right of grid
        orientation = "NORTH" # Bot always starts on the bottom middle of the grid facing north
        time_last_stopped_for_stop_sign = 0

        # loop until reaches destination
        # on each loop, it gets a new grid where it is on the bottom middle of the grid and updates the 
        # coordinates of the destination based on where it moved. it moves RESCAN_INTERVAL steps and then rescans
        while True:
            print(f"scanning...")
            origin = (GRID_SIZE - 1, 50)
            grid = get_grid()
            px.set_cam_pan_angle(0)
            path = a_star_search(grid, current_location, destination)
            print(f'{path=}')
            grid.printPath(path, destination, current_location)
            steps_to_take = path[0:RESCAN_INTERVAL]
            print(f"{steps_to_take}=")
            if len(steps_to_take) == 0:
                print('reached the destination')
                return

            if len(detections) > 0 and detections[0].label == "stop sign":
                print("stop for x seconds")
                
            px.set_dir_servo_angle(0)
            print('steps_to_take')
            print(steps_to_take)
            for step in steps_to_take:
                # first check for stop sign
                for  detection  in  detections:
                    if detection.label == "stop sign":
                        current_time = time.time()

                        if abs(current_time - time_last_stopped_for_stop_sign) >= 10: # stopped for stop sign more than 10 seconds ago
                            px.forward(0) # stop moving
                            time.sleep(3) # wait 3 seconds
                            px.forward(1) # start moving again
                            time_last_stopped_for_stop_sign = current_time # update when the last time we stopped for stop sign was
                            break

                # if changing orientation, needs to turn 90 degrees left or right
                # todo: need to improve the turning for reorient_right and reorient_left, these functions are responsible for making 90 degree turns
                # and leaving the bot in the same spot
                print("current orientation", orientation)
                if orientation == "NORTH":
                    if step[0] == current_location[0] - 1:
                        print("north forward")
                    elif step[1] == current_location[1] - 1:
                        print("north to west")
                        orientation = "WEST"
                        reorient_left()
                    elif step[1] == current_location[1] + 1:
                        print(step)
                        print(current_location)
                        print("north to east")
                        orientation = "EAST"
                        reorient_right()
                elif orientation == "EAST":
                    if step[0] == current_location[0] - 1:
                        print("east to north")
                        orientation = "NORTH"
                        reorient_left()
                    elif step[1] == current_location[1] + 1:
                        print("east forward")
                    elif step[1] == current_location[1] - 1:
                        print("dont think this should happen, would be backwards 1")
                elif orientation == "WEST":
                    if step[0] == current_location[0] - 1:
                        print("west to north")
                        orientation = "NORTH"
                        reorient_right()
                    elif step[1] == current_location[1] + 1:
                        print("dont think this should happen, would be backwards 2")
                    elif step[1] == current_location[1] - 1:
                        print("west forward")


                px.forward(1)
                #TODO - The value in this time sleep needs to be as equivalent to 1 cm per step as possible. For the current
                #path the value should take the car from the bottom of the map to the top of the map without much space left over at the top
                time.sleep(0.179)
                px.set_dir_servo_angle(0)
                current_location = step
            px.forward(0)


            # Need to reset the orientation so it is always facing north at the end of processing a batch of steps
            # ~ print(f'reorienting from {orientation=} to north since we finished processing a batch')
            # ~ px.set_dir_servo_angle(0)
            # ~ # todo: need to fine tune this reorientation
            # ~ # if it's oriented west, at the end of the if statement it should basically be facing 90 degrees to the right of where it started and in the same spot as where it started
            # ~ # if it's oriented east, at the end of the if statement it should basically be facing 90 degrees to the left of where it started and in the same spot as where it started
            # ~ if orientation == "WEST":
                # ~ reorient_right()
            # ~ if orientation == "EAST":
                # ~ reorient_left()

            # we can't really know for sure, but we'll assume that the navigation so far has taken us to the position of the last step
            last_step = steps_to_take[-1]

            #now, since we're going to re scan the grid which means the bot will be at the bottom again, we need to update the destination
            #to be in the new spot based on the last step in the path

            print(f'bot moved from {origin=} to {last_step=}')
            delta_x = last_step[0] - origin[0]
            delta_y = last_step[1] - origin[1]

            # Update the destination based on the bot's last position
            old_destination = destination 
            destination = (destination[0] - delta_x, destination[1] - delta_y)
            print(f'{old_destination=}, {destination=}')
            print(current_location)
            if old_destination == destination:
                print('destination reached')
                break;

            current_location = origin 
    finally:
        px.forward(0)
        return

def reorient_right():
    # Move backwards, turn to the right, then go backwards again to try to end up in a similar spot
    #px.backward(5)
    #time.sleep(0.5)
    print('I should be turned right')
    px.set_dir_servo_angle(30)
    px.forward(1)
    time.sleep(4.25)
    px.set_dir_servo_angle(0)
    time.sleep(0.5)
    px.backward(1)
    time.sleep(1.2)
    px.set_dir_servo_angle(30)
    px.forward(1)
    time.sleep(4.25)
    px.set_dir_servo_angle(0)
    time.sleep(0.5)
    px.backward(1)
    time.sleep(1.2)
    px.set_dir_servo_angle(30)
    px.forward(1)
    time.sleep(3.84)
    px.set_dir_servo_angle(0)
    px.backward(1)
    #TODO - The value on this time sleep below needs to be enough to bring the car back to it's start point before the turn
    time.sleep(2.6)
    px.backward(0)
    px.forward(0)

def reorient_left():
    # Move backwards, turn to the left, then go backwards again to try to end up in a similar spot
    #px.backward(5)
    #time.sleep(0.5)
    print('I should be turned left')
    px.set_dir_servo_angle(-30)
    px.forward(1)
    time.sleep(4.25)
    px.set_dir_servo_angle(0)
    time.sleep(0.5)
    px.backward(1)
    time.sleep(1.2)
    px.set_dir_servo_angle(-30)
    px.forward(1)
    time.sleep(4.25)
    px.set_dir_servo_angle(0)
    time.sleep(0.5)
    px.backward(1)
    time.sleep(1.2)
    px.set_dir_servo_angle(-30)
    px.forward(1)
    time.sleep(3.84)
    px.set_dir_servo_angle(0)
    px.backward(1)
    #TODO - The value on this time sleep below needs to be enough to bring the car back to it's start point before the turn
    time.sleep(2.6)
    px.backward(0)
    px.forward(0)
if __name__ == "__main__":
    main()
