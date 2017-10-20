#!/usr/bin/env python
import numpy as np

def Y(u):
	return np.log(1.0+u) - np.divide(u, (1.0+u))

def delta(c):
	return (200.0/3.0)*((c*c*c)/Y(c))

def rho(x,c):
	"""rho(x)/rho_crit"""
	return delta(c)/(c*x*(1+c*x)**2.)

def rho_enc(x,c):
	"""<rho(x)>/rho_crit"""
	return np.divide(200.0, np.power(x,3.0)) * np.divide(Y(c*x), Y(c))

def m_enc(x,c):
	"""M(<x)/M_200"""
	return np.divide(Y(c*x), Y(c))

def m(x,c):
	"""M(x_{i-1} < x < x_{i})/M_200"""
	y = m_enc(x,c)
	y[1:] = np.diff(m_enc(x,c))
	return y

def splmax(x, y):
	from scipy.interpolate import InterpolatedUnivariateSpline as spline
	f = spline(x, y)
	xi = np.linspace(np.min(x), np.max(x), 10*len(x))
	yi = f(xi)
	idx = np.argmax(yi)
	return xi, yi, idx

def fit(y, f, xs, N=1):
	chi2 = np.divide(\
		[np.sum(np.power(np.log(y) - np.log(f(x)), 2.0))\
		for x in xs], N)
	ls = np.exp(-chi2)
	x, l, idx = splmax(xs, ls)
	# ls = np.divide(ls, l)
	# x_err = spline(xs, ls-1.5).roots()           #FWHM
	# x_err = (x-3.0*np.std(ls), x+3.0*np.std(ls)) #+/-3sigma
	return x[idx]
