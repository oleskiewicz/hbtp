#!/usr/bin/env python
import numpy as np

h = 0.697
Rho0 = 147.7543 #rho_crit(z = 0) in M_solar/kpc^3
OmegaM = 0.281
OmegaL = 1. - OmegaM

def rho_c(z = 0.0):
  return Rho0*(OmegaM*np.power(1.0 + z, 3.)+OmegaL)

def z(rho_c = Rho0):
  pass
