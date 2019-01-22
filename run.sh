#!/bin/sh -e

#SBATCH -n 8
#SBATCH -t 12:00:00
#SBATCH -A dp004
#SBATCH -p cosma6
#SBATCH -J hbtp_limin
#SBATCH -o ./log/%A.out
#SBATCH -e ./log/%A.err
#SBATCH --exclusive

make cmh
