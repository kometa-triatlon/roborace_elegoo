#!/usr/bin/env python

import tty, sys
import pigpio
import time
import math
import argparse
import cv2
import caffe

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
    speed_right = SPEED_RIGHT
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
    parser.add_argument('--model', default='model/deploy.prototxt')
    parser.add_argument('--weights', default='model/weights.caffemodel')
    args = parser.parse_args()

    pi = pigpio.pi()
    if pi.connected:
        try:
            init(pi)
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print "Failed to start video capture"
                exit(1)

            caffe.set_mode_cpu()
            net = caffe.Net(args.model, args.weights, caffe.TEST)
            input_h = net.blobs['data'].shape[2]
            input_w = net.blobs['data'].shape[3]
            while True:
                ret, frame = cap.read()
                if not ret:
                    print "Failed to retrieve frame"
                    break

                net.blobs['data'].data[...] = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (input_w, input_h))
                out = net.forward()
                x, y = out['pred'][0]
                update_speed(x, y)
                move(pi)

        finally:
            stop(pi)
            pi.stop()
            cap.release()

    else:
        print "Not connected to daemon, stop"
        exit()

