#!/usr/bin/env python

import tty, sys
import pigpio
import time
import math
import argparse
import cv2
import Xbox.xbox as xbox

FPS = 20
DELAY = 1.0/FPS
VIDEO_SIZE = (640, 480)

ENA = 26
ENB = 16
IN1 = 17
IN2 = 27
IN3 = 22
IN4 = 24

PWM_RANGE = 255
MAX_SPEED = PWM_RANGE
MIN_SPEED = 30

SPEED_LEFT = 0
SPEED_RIGHT = 0

def init(pi):
    pi.set_mode(ENA, pigpio.OUTPUT)
    pi.set_mode(ENB, pigpio.OUTPUT)
    pi.set_PWM_range(ENA, PWM_RANGE)
    pi.set_PWM_range(ENB, PWM_RANGE)

    pi.set_mode(IN1, pigpio.OUTPUT)
    pi.set_mode(IN2, pigpio.OUTPUT)
    pi.set_mode(IN3, pigpio.OUTPUT)
    pi.set_mode(IN4, pigpio.OUTPUT)

def move(pi):
    global SPEED_LEFT
    global SPEED_RIGHT

    speed_left = SPEED_LEFT
    #if speed_left < MIN_SPEED: speed_left = 0
    speed_right = SPEED_RIGHT
    #if speed_right < MIN_SPEED: speed_right = 0
    #if speed_right > 0 or speed_left > 0:
    print "move with speed {0}/{1}".format(speed_left, speed_right)

    if speed_left > MIN_SPEED:
        pi.set_PWM_dutycycle(ENA, speed_left)
        pi.write(IN1, 0)
        pi.write(IN2, 1)
    elif speed_left < MIN_SPEED and speed_left >= 0:
        pi.write(ENA, 1)
        pi.write(IN1, 0)
        pi.write(IN2, 0)
    elif speed_left < 0:
        pi.write(ENA, 1)
        pi.write(IN1, 1)
        pi.write(IN2, 0)

    if speed_right > MIN_SPEED:
        pi.set_PWM_dutycycle(ENB, speed_right)
        pi.write(IN3, 1)
        pi.write(IN4, 0)
    elif speed_right < MIN_SPEED and speed_left >= 0:
        pi.write(ENB, 1)
        pi.write(IN3, 0)
        pi.write(IN4, 0)
    elif speed_right < 0:
        pi.write(ENB, 1)
        pi.write(IN3, 0)
        pi.write(IN4, 1)


def stop(pi):
    pi.write(ENA, 0)
    pi.write(ENB, 0)
    pi.write(IN1, 0)
    pi.write(IN2, 0)
    pi.write(IN3, 0)
    pi.write(IN4, 0)


def update_speed(x, y):
    global SPEED_LEFT
    global SPEED_RIGHT

    if y < 0: y = 0
    throttle = math.sqrt(x*x + y*y)
    angle = x
    avg_speed = MAX_SPEED * throttle

    SPEED_RIGHT = (1 - angle) * avg_speed
    SPEED_LEFT = (1 + angle) * avg_speed

    if SPEED_LEFT > MAX_SPEED: SPEED_LEFT = MAX_SPEED
    if SPEED_RIGHT > MAX_SPEED: SPEED_RIGHT = MAX_SPEED    

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
        
    pi = pigpio.pi()
    if pi.connected:
        try:
            init(pi)
            joy = xbox.Joystick()
            if args.record:
                cap = cv2.VideoCapture(0)
                log = open('recording/log.csv', 'w')
                log.write('frame,x,y\n')
                #fourcc = cv2.cv.CV_FOURCC(*'DIVX')
                #out = cv2.VideoWriter('/home/pi/rc_car/recording.avi', fourcc, FPS, VIDEO_SIZE)

            frameno = 0
            while True:
                (x, y) = joy.rightStick()
                update_speed(x, y)
                move(pi)
                if args.record:
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret: #out.write(frame)
                            frameid = '%04d' % (frameno)
                            cv2.imwrite('recording/' + frameid + '.jpg', frame)
                            log.write('{0},{1},{2}\n'.format(frameid, x, y))
                            frameno += 1
                
                time.sleep(DELAY)

        finally:
            stop(pi)
            pi.stop()
            joy.close()
            if args.record:
                cap.release()
                log.close()
                #out.release()
    else:
        print "Not connected to daemon, stop"
        exit()

