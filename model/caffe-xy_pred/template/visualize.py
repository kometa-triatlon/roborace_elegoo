#!/usr/bin/env python

import os
import h5py
import argparse
import caffe
import numpy as np
import cv2

def draw_pred(frame, w, h, x_gt, x_pred):
    center_x = w/2
    center_y = h - 10
    bar_h = 10
    bar_max_w = 80
    color_gt = (0, 255, 0)
    color_pred = (255, 0, 0)
    bar_gt_w = int(bar_max_w * -x_gt)
    if bar_gt_w == 0: bar_gt_w = 1
    bar_pred_w = int(bar_max_w * -x_pred)
    if bar_pred_w == 0: bar_pred_w = 1
    print "x_gt=%.2f, x_pred=%.2f" % (x_gt, x_pred)
    bar_gt = [[center_x - bar_gt_w, center_y - bar_h], [center_x, center_y - bar_h], [center_x, center_y], [center_x - bar_gt_w, center_y]]
    bar_pred = [[center_x - bar_pred_w, center_y], [center_x, center_y], [center_x, center_y + bar_h], [center_x - bar_pred_w, center_y + bar_h]]
    cv2.fillConvexPoly(frame, np.asarray(bar_gt), (0, 255, 0))
    cv2.fillConvexPoly(frame, np.asarray(bar_pred), 2)
    return frame

if __name__ == '__main__':
    model = 'deploy.prototxt'
    weights = 'final.caffemodel'
    h5path = open('validdat.txt').readlines()[0].strip()
    f = h5py.File(h5path, 'r')
    data = f['data']
    labels = f['label']

    imheight = data[0, :, :, :].shape[1]
    imwidth = data[0, :, :, :].shape[2]

    caffe.set_mode_gpu()
    net = caffe.Net(model, weights, caffe.TEST)

    num = data.shape[0]
    for i in range(num):
        frame = data[i, :, :, :]
        gt = labels[i]
        net.blobs['data'].data[...] = frame
        out = net.forward()
        frame = draw_pred(frame[0, :, :], imwidth, imheight, gt, out['fc2'][0][0])
        cv2.imshow('Prediction', frame)
        cv2.waitKey(200)

    cv2.destroyAllWindows()
