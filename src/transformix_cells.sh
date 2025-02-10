#!/bin/bash
#BSUB -n 4
#BSUB -W 10:00
#BSUB -o log_%J.txt

source activate base
conda activate cm2

ARG1=${1:-''}
ARG2=${2:-''}
ARG3=${3:-''}
ARG4=${4:-''}

echo "folder from elastix output containing TransformParameters files: $ARG1"
echo "csv file containing points in fixed volume space: $ARG2"
echo "moving image: $ARG3"
echo "output directory (optional): $ARG4"

python transformix_points.py "$ARG1" "$ARG2" "$ARG3" "$ARG4"
