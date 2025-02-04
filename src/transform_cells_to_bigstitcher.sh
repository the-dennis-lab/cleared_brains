#!/bin/bash
#BSUB -n 4
#BSUB -W 10:00
#BSUB -o log_%J.txt

source activate base
conda activate cm2

echo 'activated cm2'
echo 'using variables:'
echo $1
python filtcells_to_locs.py $1

cd ../../BigStit*

for i in {0..30};
do (./transform-points --csvIn="${1}/outputs/s${i}_filtered_cells.csv" --xml="${1}dataset.xml" -vi="0,${i}" --csvOut="${1}/outputs/s${i}_bigstitcher_out.txt" | tail -1);
done

for i in {0..30};
do (./transform-points -p=0,0,0 --xml="${1}dataset.xml" -vi="0,${i}");
done
