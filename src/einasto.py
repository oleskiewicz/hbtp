#!/usr/bin/env python
import numpy as np
from scipy.special import gammainc

def rho_enc(x, c, a):
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
	from scipy.interpolate import interp2d
	xi = np.linspace(np.min(x), np.max(x), 10*len(x))
	yi = np.linspace(np.min(y), np.max(y), 10*len(y))
	f = interp2d(x, y, z, kind='cubic')
	zi = f(xi, yi)
	idx = np.unravel_index(np.argmax(zi), zi.shape)
	return xi, yi, zi, idx

def fit(z, f, xs, ys, N=1):
	"""Maximise likelihood :math:`L = e^{-\chi^2}`"""
	chi2 = np.divide(\
		[[np.sum(np.power(np.log(z) - np.log(f(x, y)), 2.0))\
		for y in ys] for x in xs], N)
	ls = np.exp(-chi2)
	x, y, l, idx = splmax(xs, ys, ls)
	return x[idx[0]], y[idx[1]]
