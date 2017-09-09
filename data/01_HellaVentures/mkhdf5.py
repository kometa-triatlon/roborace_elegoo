#!/usr/bin/env python
import os
import numpy as np
import caffe
import pandas as pd
import h5py

IMG_CHANNELS = 1
IMG_HEIGHT = 240
IMG_WIDTH  = 320
train_sets = ['01', '02', '03', '05', '06']
valid_sets = ['04']


def load(sets):
    num_samples = 0
    dataframes = list()
    for setid in sets:
        d = pd.read_csv(os.path.join('src', setid, 'log.csv'), dtype={'frame': str, 'x': np.float32, 'y': np.float32})
        num_samples += d.shape[0]
        print("{} samples in set {}".format(d.shape[0], setid))
        dataframes.append((setid, d))

    data = np.zeros((num_samples, IMG_CHANNELS, IMG_HEIGHT, IMG_WIDTH), dtype=np.float32)
    label = np.zeros((num_samples, 2), dtype=np.float32)

    sampleid = 0
    for setid, d in dataframes:
        print("Reading set {}".format(setid))
        for _, row in d.iterrows():
            framepath = os.path.join('src', setid, row['frame'] + '.jpg')
            if not os.path.isfile(framepath):
                raise IOError("{} not found".format(framepath))

            frame = caffe.io.load_image(framepath, color=False)
            frame = caffe.io.resize_image(frame, (IMG_HEIGHT, IMG_WIDTH))
            data[sampleid, :, :, :] = frame.transpose([2, 0, 1]) # TODO: subtract mean
            label[sampleid, 0] = row['x']
            label[sampleid, 1] = row['y']
            sampleid += 1

    return data, label

if __name__ == '__main__':
    data_valid, label_valid = load(valid_sets)
    dest_dir = "hdf5_xy_%dch_%dx%d" % (IMG_CHANNELS, IMG_WIDTH, IMG_HEIGHT)
    if not os.path.isdir(dest_dir): os.makedirs(dest_dir)
    with h5py.File(os.path.join(dest_dir, 'valid.h5'), 'w') as f:
        f.create_dataset('data', data=data_valid, compression='gzip', compression_opts=1)
        f.create_dataset('label', data=label_valid, compression='gzip', compression_opts=1)

    data_train, label_train = load(train_sets)
    with h5py.File(os.path.join(dest_dir, 'train.h5'), 'w') as f:
        f.create_dataset('data', data=data_train, compression='gzip', compression_opts=1)
        f.create_dataset('label', data=label_train, compression='gzip', compression_opts=1)
