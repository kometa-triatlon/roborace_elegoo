#!/usr/bin/env python

import tty, sys
import pigpio
import time

ENA = 26
ENB = 16
IN1 = 17
IN2 = 27
IN3 = 22
IN4 = 24

PWM_RANGE = 255
MAX_SPEED = PWM_RANGE
MIN_SPEED = 80

SPEED_LEFT = 0
SPEED_RIGHT = 0
ACC = 10

def getch():
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

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
    if speed_left < MIN_SPEED: speed_left = 0
    speed_right = SPEED_RIGHT
    if speed_right < MIN_SPEED: speed_right = 0
    print "move with speed {0}/{1}".format(SPEED_LEFT, SPEED_RIGHT)
    pi.set_PWM_dutycycle(ENA, speed_left)
    pi.set_PWM_dutycycle(ENB, speed_right)

    pi.write(IN1, 0)
    pi.write(IN2, 1)
    pi.write(IN3, 1)
    pi.write(IN4, 0)

def stop(pi):
    pi.write(ENA, 0)
    pi.write(ENB, 0)
    pi.write(IN1, 0)
    pi.write(IN2, 0)
    pi.write(IN3, 0)
    pi.write(IN4, 0)


def update_speed(ch):
    global SPEED_LEFT
    global SPEED_RIGHT
    global ACC

    if ch == 'w':
        SPEED_LEFT  += ACC
        SPEED_RIGHT += ACC
    elif ch == 'a':
        SPEED_LEFT  -= ACC
        SPEED_RIGHT += ACC
    elif ch == 'd':
        SPEED_LEFT  += ACC
        SPEED_RIGHT -= ACC
    elif ch == 's':
        SPEED_LEFT  -= ACC
        SPEED_RIGHT -= ACC    

    if SPEED_LEFT < 0: SPEED_LEFT = 0
    if SPEED_LEFT > MAX_SPEED: SPEED_LEFT = MAX_SPEED
    if SPEED_RIGHT < 0 : SPEED_RIGHT = 0
    if SPEED_RIGHT > MAX_SPEED: SPEED_RIGHT = MAX_SPEED
    

if __name__ == '__main__':

    pi = pigpio.pi()
    if pi.connected:
        try:
            init(pi)
            while True:
                ch = getch()
                if ch == 'q': break
                else: update_speed(ch)
                move(pi)

        finally:
            stop(pi)
            pi.stop()
    else:
        print "Not connected to daemon, stop"
        exit()

