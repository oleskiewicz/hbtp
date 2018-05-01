#!/usr/bin/env python
import numpy as np


def Y(u):
    return np.log(1.0 + u) - np.divide(u, (1.0 + u))


def delta(c):
    return (200.0 / 3.0) * (np.power(c, 3.0) / Y(c))


def rho(x, c):
    """rho(x)/rho_crit"""
    return delta(c) / (c * x * np.power(1.0 + c * x, 2.0))


def rho_enc(x, c):
    """<rho(x)>/rho_crit"""
    return np.divide(200.0 * Y(c * x), np.power(x, 3.0) * Y(c))


def m(x, c):
    """M(<x)/M_200"""
    return np.divide(Y(c * x), Y(c))


def m_diff(x, c):
    """M(x_{i-1} < x < x_{i})/M_200"""
    y = m(x, c)
    y[1:] = np.diff(m(x, c))
    return y


# def fit(f, xs, ys):
#     """chi2 fit.
#     """
#     chi2 = np.divide(
#         [np.sum(np.power((ys - f(x)), 2.0)) for x in xs],
#         len(ys)-1)
#     i = np.argmin(chi2)
#     return xs[i], chi2[i]
