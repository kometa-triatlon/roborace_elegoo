#!/usr/bin/env python
import os
import numpy as np
import caffe
import pandas as pd
import h5py
import argparse

def load(sets, srcdir, img_height, img_width):
    num_samples = 0
    dataframes = list()
    for setid in sets:
        d = pd.read_csv(os.path.join(srcdir, setid, 'log.csv'), dtype={'frame': str, 'x': np.float32, 'y': np.float32})
        num_samples += d.shape[0]
        print("{} samples in set {}".format(d.shape[0], setid))
        dataframes.append((setid, d))

    num_channels = 1
    data = np.zeros((num_samples, num_channels, img_height, img_width), dtype=np.float32)
    label = np.zeros((num_samples, 2), dtype=np.float32)

    sampleid = 0
    for setid, d in dataframes:
        print("Reading set {}".format(setid))
        for _, row in d.iterrows():
            framepath = os.path.join(srcdir, setid, row['frame'] + '.jpg')
            if not os.path.isfile(framepath):
                raise IOError("{} not found".format(framepath))

            frame = caffe.io.load_image(framepath, color=False)
            frame = caffe.io.resize_image(frame, (img_height, img_width))
            data[sampleid, :, :, :] = frame.transpose([2, 0, 1])
            label[sampleid, 0] = row['x']
            label[sampleid, 1] = row['y']
            sampleid += 1

    return data, label # mean

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src_dir', default='src')
    parser.add_argument('--dest_dir')
    parser.add_argument('--train_sets', nargs='+')
    parser.add_argument('--valid_sets', nargs='+')
    parser.add_argument('--img_width', type=int, default=320)
    parser.add_argument('--img_height', type=int, default=240)
    args = parser.parse_args()

    data_valid, label_valid = load(args.valid_sets, args.src_dir, args.img_height, args.img_width)

    if not os.path.isdir(args.dest_dir): os.makedirs(args.dest_dir)
    with h5py.File(os.path.join(args.dest_dir, 'valid.h5'), 'w') as f:
        f.create_dataset('data', data=data_valid, compression='gzip', compression_opts=1)
        f.create_dataset('label', data=label_valid, compression='gzip', compression_opts=1)

    data_train, label_train = load(args.train_sets, args.src_dir, args.img_height, args.img_width)
    with h5py.File(os.path.join(args.dest_dir, 'train.h5'), 'w') as f:
        f.create_dataset('data', data=data_train, compression='gzip', compression_opts=1)
        f.create_dataset('label', data=label_train, compression='gzip', compression_opts=1)
