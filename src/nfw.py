#!/usr/bin/env python
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline as spline

# helper function
def __m(x,c):
	return np.power(10.0, m(np.log10(x),c))
def __cumdiff(y):
	yd = y.copy()
	yd[1:] = np.diff(y)
	return yd
def __Y(u):
	return (np.log(1.0+u) - (u/(1.0+u)))
def __delta_c(c):
	return (200./3.)*((c**3.)/__Y(c))

def __spline_max(x, y):
	y_spl = spline(x, y)
	x_spl = np.linspace(np.min(x), np.max(x), 10*len(x))
	y_spl = y_spl(x_spl)
	spl_idx = np.argmax(y_spl)
	return x_spl[spl_idx], y_spl[spl_idx]

def fit(x, y):
	nc, c_min, c_max = 1000, 1.0, 10.0
	cc = np.linspace(c_min, c_max, nc)
	chi2 = np.zeros(nc)
	ll = np.zeros(nc)
	for i in range(nc):
		for j,_ in enumerate(x):
			chi2[i] += np.power(np.log10(y[j]) - np.log10(m_diff(x, cc[i])[j]), 2.0)
		ll[i] = np.exp(-chi2[i])
	c, l_max = __spline_max(cc, ll)
	ll /= l_max
	c_err = spline(cc, ll-0.5).roots() #FWHM
	# c_err = (c-3.0*np.std(ll), c+3.0*np.std(ll)) #+/-3sigma
	return c, c_err

def rho(x,c):
	return __delta_c(c)/(c*x*(1+c*x)**2.)

def rho_enc(x,c):
	return ((200./np.power(x,3.0))*(__Y(c*x)/__Y(c)))

def m(x,c):
	return np.log10((np.log(1.+c*(10.**x)) - (c*(10.**x)/(1.+c*(10.**x))))/(np.log(1.+c) - (c/(1.+c))))

def m_diff(x,c):
	return __cumdiff(__m(x,c))
