from picarx import Picarx
import time
import random

# Portions of this code were based off of picar-x examples. Specifically, the avoiding_obstacles.py example
# which was used to gain an understanding of how to program movement of the motor and how to receive input from
# the ultrasonic sensor. The stare_at_you.py picar-x example was used to gain an understanding of how to program
# movement of the camera servos to allow the ultrasonic sensor to scan back and forth.
POWER = 50
SafeDistance = 40   # > 40 safe
DangerDistance = 20 # > 20 && < 40 turn around, 
                    # < 20 backward

# The maximum rotation of the drive servos is from -30 to 30, so sticking with those two numbers for turning
DirectionList = [-30,30]

def handle_obstacle_random(px):
    px.forward(0)
    px.backward(0)
    px.set_dir_servo_angle(0)
    # Scan left and right to check for clearest path
    # Scan left first
    # Left distance (-35)
    px.set_cam_pan_angle(-35)
    left_distance = px.ultrasonic.read()
    print("left_distance: ",left_distance)
    time.sleep(0.5)
    
    # Set camera angle back to zero
    px.set_cam_pan_angle(0)
    time.sleep(0.5)

    # Scan right next
    # Right distance (35)
    px.set_cam_pan_angle(35)
    right_distance = px.ultrasonic.read()
    print("right_distance: ",right_distance)
    time.sleep(0.5)
    
    # Set camera angle back to zero
    px.set_cam_pan_angle(0)
    time.sleep(0.5)

    # If neither safe direction is safe, backup
    if left_distance >= DangerDistance and left_distance < SafeDistance and right_distance >= DangerDistance and right_distance < SafeDistance:
        print("neither")
        px.set_dir_servo_angle(random.choice(DirectionList))
        px.backward(POWER * 2)
        time.sleep(0.5)
        px.backward(0)
        time.sleep(0.5)
    # Else if both directions are safe, choose a random direction
    elif left_distance >= SafeDistance and right_distance >= SafeDistance :
        print("either")
        px.set_dir_servo_angle(random.choice(DirectionList))
        px.forward(POWER)
        time.sleep(0.5)
    # Else if the left turn is safe and the right turn isn't, choose the left turn
    elif left_distance >= SafeDistance and right_distance < SafeDistance :
        print("left")
        px.set_dir_servo_angle(-30)
        px.forward(POWER)
        time.sleep(0.5)
    # Else if the right turn is safe and the left turn isn't, choose the right turn
    elif right_distance >= SafeDistance and left_distance < SafeDistance :
        print("right")
        px.set_dir_servo_angle(30)
        px.forward(POWER)
        time.sleep(0.5)
    #If no clear path exists, back up
    else:
        print("backup")
        px.set_dir_servo_angle(0)
        px.backward(POWER * 2)
        time.sleep(0.5)
        px.backward(0)
        time.sleep(0.5)

    return

def main():
    try:
        px = Picarx(ultrasonic_pins=['D2','D3'])
        px.set_cam_tilt_angle(15)
        distance = 0
       
        while True:
            px.set_cam_pan_angle(0)
            distance = px.ultrasonic.read()
            print("distance: ",distance)
            # While testing my car, my ultrasonic sensor would often produce negative readings (generally -1 or -2).
            # These readings could occur in the middle of the room or when right next to an obstacle. In order to try to fix this,
            # I have the car move forward or backward in a random direction until it picks up a good reading.
            reading_count = 0
            while distance < 0:
                px.forward(0)
                px.backward(0)
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
                distance = px.ultrasonic.read()
            reading_count = 0
            # The following if/else if/else statement came from the same statement in the avoiding_obstacles.py example
            # Move forward in a straight line if able to do so
            if distance >= SafeDistance:
                print("safe")
                px.set_dir_servo_angle(0)
                px.forward(POWER)
            # If unable to move forward in a straight line, turn in a random direction
            elif distance >= DangerDistance:
                print("turn")
                handle_obstacle_random(px)
            # If unable to turn because the car is too close to an obstacle, back up
            else:
                print("backup main")
                px.set_dir_servo_angle(random.choice(DirectionList))
                px.backward(POWER * 2)
                time.sleep(0.5)
                px.backward(0)
                time.sleep(0.5)

    finally:
        px.forward(0)


if __name__ == "__main__":
    main()
