#!/bin/bash
export PATH=/Users/dprylipko/Work/caffe/build/tools/:$PATH

caffe train --solver solver.prototxt -log_dir log
