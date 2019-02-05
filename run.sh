#!/bin/sh -e

#SBATCH -n 8
#SBATCH -t 12:00:00
#SBATCH -A durham
#SBATCH -p cosma
#SBATCH -J hbtp_limin
#SBATCH -o ./log/%A.out
#SBATCH -e ./log/%A.err
#SBATCH --exclusive

make cmh
