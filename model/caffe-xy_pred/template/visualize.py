#!/usr/bin/env python

import os
import h5py
import argparse
import caffe
import numpy as np
import cv2

def draw_pred(frame, w, h, gt, pred):
    center = (int(w/2), int(h - 50))
    max_r = 50
    cv2.circle(frame, center, max_r, (0, 0, 0))
    cv2.circle(frame, center, 1, (0, 0, 0))

    gt_point = ( int(center[0] +  max_r * gt[0]), int(center[1] - max_r * gt[1]))
    pred_point = ( int(center[0] +  max_r * pred[0]), int(center[1] - max_r * pred[1]))

    cv2.circle(frame, gt_point, 2, (0, 0, 0), 2)
    cv2.circle(frame, pred_point, 2, (255, 255, 255), 2)

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
        gt = labels[i, :]
        net.blobs['data'].data[...] = frame
        out = net.forward()
        frame = draw_pred(frame[0, :, :], imwidth, imheight, gt, out['pred'][0])
        cv2.imshow('Prediction', frame)
        cv2.waitKey(200)

    cv2.destroyAllWindows()
