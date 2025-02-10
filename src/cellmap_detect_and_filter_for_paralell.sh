#!/bin/bash
#BSUB -n 40
#BSUB -W 10:00
#BSUB -o log_%J.txt


cd /groups/dennis/dennislab/dennise/github/ClearMap2/ClearMap/Scripts

source activate base
conda activate cm2

echo 'activated cm2'
echo 'using variables:'
echo $1
python CellMap_parallel.py $1
echo 'complete?'
rm $1/tiffs/tif*tif
