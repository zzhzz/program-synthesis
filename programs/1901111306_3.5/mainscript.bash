#!/bin/bash

. /home/zwj/miniconda3/etc/profile.d/conda.sh
conda activate /home/zwj/miniconda3/envs/sygus
exec /home/zwj/miniconda3/envs/sygus/bin/python "$1/realmain.py" "$2" "$1"
