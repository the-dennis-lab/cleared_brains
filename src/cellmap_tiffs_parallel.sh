#!/bin/bash
#BSUB -n 1
#BSUB -W 10:00
#BSUB -o log_%J.txt

conda init
conda activate cm2
echo 'activated cm2'
cd /groups/dennis/dennislab/dennise/github/ClearMap2/ClearMap/Scripts
echo 'in wd'
echo $1


for i in $(seq 0 9); do
bsub -o jobs$1 python CellMap_parallel_tiffs.py $1 "dataset.h5" s0$i
done

for i in $(seq 10 30); do
bsub -o jobs$1 python CellMap_parallel_tiffs.py $1 "dataset.h5" s$i
done

echo 'complete?'
