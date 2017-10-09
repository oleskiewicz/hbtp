#!/usr/bin/env python
import numpy as np
from scipy.special import gammainc

def rho_enc(x,c,a):
	"""<rho(x)>/rho_crit"""
	return np.divide(\
		200.0 * gammainc(3.0/a, (2.0/a)*np.power(c*x, a)),
		np.power(x,3.0) * gammainc(3.0/a, (2.0/a)*np.power(c, a)))

def m_enc(x, c, a):
	"""M(<x)/M_200"""
	return np.divide(\
		gammainc(3.0/a, (2.0/a)*np.power(c*x, a)),
		gammainc(3.0/a, (2.0/a)*np.power(c, a)))

def m(x, c, a):
	"""M(x_{i-1} < x < x_{i})/M_200"""
	y = m_enc(x, c, a)
	y[1:] = np.diff(m_enc(x, c, a))
	return y

def splmax(x, y, z):
	from scipy.interpolate import griddata
	xy = np.transpose([np.tile(x, len(y)), np.repeat(y, len(x))])
	grid_x, grid_y = np.meshgrid(\
		np.linspace(np.min(x),np.max(x), len(x)*10),
		np.linspace(np.min(y),np.max(y), len(y)*10))
	grid_z = griddata(xy, z, (grid_x, grid_y), method='cubic')
	idx = np.unravel_index(np.argmax(interpolated_z), interpolated_z.shape)
	return xy[idx[1]], xy[idx[0]], grid_z[idx]

def fit(z, f, xs, ys, N=1):
	chi2 = np.divide(\
		[[np.sum(np.power(np.log(z) - np.log(f(x, y)), 2.0))\
		for x in xs] for y in ys], N)
	ls = np.exp(-chi2)
	x, y, l = splmax(xs, ys, ls)
	return ls

# c, a = fit(p, lambda c, a: m(np.power(10.0,x), c, a),\
# 		np.linspace(1.0, 10.0, 10), np.linspace(0.1, 1.0, 10))

