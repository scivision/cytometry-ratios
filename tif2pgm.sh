#!/bin/bash

cd ../data

for f in FRAME_14*.tif
do
  convert "$f" -compress none "${f%tif}pgm"
done

