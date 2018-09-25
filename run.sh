#!/bin/sh -ex

#SBATCH -n 16
#SBATCH -t 1440
#SBATCH -P dp004
#SBATCH -q cosma
#SBATCH -j hbtp_cmh
#SBATCH -o ./log/%j.txt
#SBATCH -e ./log/%j.txt
#SBATCH --exclusive

make split
