#!/bin/sh -e

#SBATCH -n 16
#SBATCH -t 1440
#SBATCH -P dp004
#SBATCH -q cosma
#SBATCH -j hbtp_limin
#SBATCH -o ./log/%j.txt
#SBATCH -e ./log/%j.txt
#SBATCH --exclusive

make all
