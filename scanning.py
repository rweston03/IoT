from picarx import Picarx
import time
import argparse
import random

POWER = 50
SafeDistance = 40   # > 40 safe
DangerDistance = 20 # > 20 && < 40 turn around, 
                    # < 20 backward

# The maximum rotation of the drive servos is from -30 to 30, so sticking with those two numbers for turning
DirectionList = [-30,30]


def handle_obstacle_path(distance, pattern):
    # Scan left to right to check for clear path
    # If clear path exists, set chosen re-route and re-route distance init
        # Scan to original path direction and see if still blocked
        # While still blocked, 
    # While no clear path exists, back up and scan again
    
    return True

def handle_obstacle_random(px):
    px.forward(0)
    # Scan left to right to check for clearest path
    # Left distance (-35)
    px.set_cam_pan_angle(-35)
    left_distance = round(px.ultrasonic.read(), 0)
    print("left_distance: ",left_distance)
    time.sleep(0.5)
    
    px.set_cam_pan_angle(0)
    time.sleep(0.5)

    # Right distance (35)
    px.set_cam_pan_angle(35)
    right_distance = round(px.ultrasonic.read(), 0)
    print("right_distance: ",right_distance)
    time.sleep(0.5)
    
    px.set_cam_pan_angle(0)
    time.sleep(0.5)

    # If neither safe, backup
    if left_distance >= DangerDistance and left_distance < SafeDistance and right_distance >= DangerDistance and right_distance < SafeDistance:
        print("neither")
        px.set_dir_servo_angle(0)
        time.sleep(0.5)
        px.set_dir_servo_angle(random.choice(DirectionList))
        px.backward(POWER * 2)
        time.sleep(0.5)
    # Else if negligable difference, choose random
    elif left_distance >= SafeDistance and right_distance >= SafeDistance :
        print("either")
        px.set_dir_servo_angle(0)
        time.sleep(0.5)
        px.set_dir_servo_angle(random.choice(DirectionList))
        px.forward(POWER)
        time.sleep(0.5)
    # Else choose clear path
    elif left_distance >= SafeDistance and right_distance < SafeDistance :
        print("left")
        px.set_dir_servo_angle(0)
        time.sleep(0.5)
        px.set_dir_servo_angle(-30)
        px.forward(POWER)
        time.sleep(0.5)
    elif right_distance >= SafeDistance and left_distance < SafeDistance :
        print("right")
        px.set_dir_servo_angle(0)
        time.sleep(0.5)
        px.set_dir_servo_angle(30)
        px.forward(POWER)
        time.sleep(0.5)
    #If no clear path exists, back up
    else:
        print("backup")
        px.set_dir_servo_angle(0)
        px.backward(POWER)
        px.backward(POWER)
        px.backward(POWER)
        time.sleep(0.5)

    return

def main():
    try:
        parser=argparse.ArgumentParser()
        parser.add_argument("pattern", choices=['random', 'zigzag', 'path', 'none'], default = 'none')
        args=parser.parse_args()
        print("chosen pattern: ", (args.pattern if args.pattern is not None else 'none'))

        px = Picarx()
        # px = Picarx(ultrasonic_pins=['D2','D3']) # tring, echo
        px.set_cam_tilt_angle(0)
        previous_distance = 0
        distance = 0
       
        while True:
            pattern = args.pattern if args.pattern is not None else 'none'
            px.set_cam_pan_angle(0)
            previous_distance = distance
            distance = round(px.ultrasonic.read(), 2)
            print("distance: ",distance)
            reading_count = 0
            while distance < 0:
                px.forward(0)
                print("error distance: ",distance)
                reading_count += 1
                if reading_count % 2 == 0:
                    px.set_dir_servo_angle(random.choice(DirectionList))
                    px.forward(POWER)
                    time.sleep(0.5)
                elif reading_count % 2 == 1:
                    px.set_dir_servo_angle(random.choice(DirectionList))
                    px.backward(POWER)
                    time.sleep(0.5)
                distance = round(px.ultrasonic.read(), 2)
            reading_count = 0

            if distance >= SafeDistance:
                print("safe")
                px.set_dir_servo_angle(0)
                px.forward(POWER)
            elif distance >= DangerDistance:
                print("turn")
                handle_obstacle_random(px)
            else:
                print("backup main")
                px.set_dir_servo_angle(random.choice(DirectionList))
                px.backward(POWER)
                time.sleep(0.5)

    finally:
        px.forward(0)


if __name__ == "__main__":
    main()