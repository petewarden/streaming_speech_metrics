#!/bin/bash -ex

tmpdir=`mktemp -d`
python video_from_transcripts.py $1 ${tmpdir}

AUDIO_FILE=`python -c "import utils;print(utils.flac_file_name_from_file_id('$1'))"`

ffmpeg -framerate 30 -pattern_type glob -i "${tmpdir}/*.png" -i ${AUDIO_FILE} -c:v libx264 -pix_fmt yuv420p $1.mp4

open $1.mp4