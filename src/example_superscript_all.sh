ANN_VOL=${1:-''}
ANN_CSV=${2:-''}
ANN_MASK=${3:-''}
MV_VOL=${4:-''}
FX_VOL=${5:-''}
BASENAME=${6:-''}
BRAIN_VOL="/groups/dennis/dennislab/Imaging/raw_imaging_data/${6:-''}/processed/bigstitcher"
CCF_TO_BRAIN_FLD="${BRAIN_VOL}/output_axial_allenCCF_25_${6:-''}"
TXT_FILE="${BRAIN_VOL}/outputs/filtered_cells_for-transformix.txt"
OUTPUT_DIR="${BRAIN_VOL}/outputs"

echo "basename: $BASENAME"
echo "annotation volume: $ANN_VOL"
echo "annotation labels: $ANN_CSV"
echo "annotation mask volume: $ANN_MASK"
echo "mv: $MV_VOL"
echo "fx: $FX_VOL"
echo "processed/bigstitcher folder: $BRAIN_FLD"

echo "elastix folder output: $CCF_TO_BRAIN_FLD"
echo "currently non existant file for transformix: $TXT_FILE"
echo "transformix_out folder: $OUTPUT_DIR"


#bsub -J "elastix_${BASENAME}" -o "logs/elastix_${BASENAME}.txt" -n 2 ./0_elastix_run.sh ${MV_VOL} ${FX_VOL}
bsub -J "fuse_${BASENAME}" -o "logs/fused_${BASENAME}.txt" -n 40 ./1_fuse_volume.sh ${BASENAME}
bwait -w "ended(fuse_${BASENAME})"
bsub -n 1 -o "logs/launchtiffjobs_${BASENAME}.txt" -J "launchtiff_${BASENAME}" ./2_cellmap_tiffs_parallel.sh ${BRAIN_FLD} ${BASENAME}
bwait -w "ended(launchtiff_${BASENAME})"
echo "entering waiting loop"
for i in {0..23}; do
   echo "waiting for ${i}"
   bwait -w "ended(maketiffs_${BASENAME}_${i})"
done
echo "finished maketiffs, starting detect and filter (GPUs)"
bsub -J "babysit_${BASENAME}" -o "/groups/dennis/dennislab/dennise/github/cleared_brains/src/logs/babysit_${BASENAME}.txt" -n 1 ./3_1_checktiffs.sh ${BRAIN_FLD} ${BASENAME}
sleep 1m
bwait -w "ended(babysit_${BASENAME})"
bsub -J "stitchonly_${BASENAME}" -n 36 -q gpu_a100 -gpu "num=3" -o "logs/stitchonlymonitor_${BASENAME}.txt" ./3_2_cellmap_stitchonly.sh $BRAIN_FLD
sleep 1m
bwait -w "ended(stitchonly_${BASENAME})"
bsub -J "detectsingle_${BASENAME}" -n 50  -o "logs/detectsingle_${BASENAME}.txt" ./3_3_cellmap_detectsingle.sh $BRAIN_FLD
sleep 1m
echo "finished detect, prepping for transformix"
bsub -J "prep-for-transformix_${BASENAME}" -n 1 -o "logs/prepfortransformix_${BASENAME}.txt" ./4_prep_for_transformix.sh $BRAIN_FLD
sleep 1m
bwait -w "ended(prep-for-transformix_${BASENAME})"
echo "finished prepping, now running transformix"
bsub -J "transformix_${BASENAME}" -o "logs/transformix_${BASENAME}.txt" -n 2 ./5_transformix_cells.sh $CCF_TO_BRAIN_FLD $TXT_FILE $MV_VOL
sleep 1m
bwait -w "ended(transformix_${BASENAME})"
echo "finished transformix, formatting final ouputs"
bsub -J "post_transformix_${BASENAME}" -o "logs/posttransformix_${BASENAME}.txt" -n 40 ./6_post_transformix.sh $OUTPUT_DIR $ANN_VOL $ANN_CSV $ANN_MASK
sleep 1m
bwait -w "ended(post_transformix_${BASENAME})"
echo "complete! probably"
