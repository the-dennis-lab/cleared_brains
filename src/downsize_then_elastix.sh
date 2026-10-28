source ./config_file.sh

INPUT_FLD=${1:-''}
MV_VOL=${2:-''}
#FX_VOL=${3:-''}
#OUTPUT_DIR=${4:-''}

echo "path to environment: $ENV_PATH"
echo "input fld: $INPUT_FLD"
echo "mv: $MV_VOL"
#echo "fx: $FX_VOL"
#echo "using all four transforms"
#echo "output dir (optional): $OUTPUT_DIR"
#echo "annotation volume (optional): $ANN_VOL"

# TODO LATER, automate both steps
#bsub -J "stack_" -o "logs/fused_${BASENAME}.txt" -n 40 ./1_fuse_volume.sh >
#bwait -w "ended(fuse_${BASENAME})"
#bsub -n 1 -o "logs/launchtiffjobs_${BASENAME}.txt" -J "launchtiff_${BASENAME}" ./2_c>

$ENV_PATH tiffs_to_stack.py "$INPUT_FLD" "$MV_VOL"
#$ENV_PATH elastix_mv_to_fx.py "$MV_VOL" "$FX_VOL" "4" "$OUTPUT_DIR" "$ANN_VOL"


