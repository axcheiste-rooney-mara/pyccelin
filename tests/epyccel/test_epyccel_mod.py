# pylint: disable=missing-function-docstring, missing-module-docstring
import os
import sys
from numpy.random import randint, uniform
from numpy import allclose

from pyccel.epyccel import epyccel

# Relative and absolute tolerances for array comparisons in the form
# numpy.isclose(a, b, rtol, atol). Windows has larger round-off errors.
if sys.platform == 'win32':
    RTOL = 1e-13
    ATOL = 1e-14
elif os.environ.get('PYCCEL_DEFAULT_COMPILER', 'GNU') == 'intel':
    RTOL = 1e-11
    ATOL = 1e-14
else:
    RTOL = 2e-14
    ATOL = 1e-15

def test_modulo_int_int(language):
    def modulo_i_i(x : int, y : int):
        return x % y, x % -y, -x % y, -x % -y, y % -y, -y % y

    f = epyccel(modulo_i_i, language=language)
    x = randint(0, 1e6)
    y = randint(1, 1e6)


    f_output = f(x, y)
    modulo_i_i_output = modulo_i_i(x, y)
    assert modulo_i_i_output == f_output
    assert isinstance(f_output, type(modulo_i_i_output))

def test_modulo_real_real(language):
    def modulo_r_r(x : 'float', y : 'float'):
        return x % y, x % -y, -x % y, -x % -y, y % -y, -y % y

    f = epyccel(modulo_r_r, language=language)
    x = uniform(low=0, high=1e6)
    y = uniform(low=1, high=1e2)

    f_output = f(x, y)
    modulo_r_r_output = modulo_r_r(x, y)
    assert allclose(f_output, modulo_r_r_output, rtol=RTOL, atol=ATOL)
    assert isinstance(f_output, type(modulo_r_r_output))

def test_modulo_real_int(language):
    def modulo_r_i(x : 'float', y : 'int'):
        return x % y, x % -y, -x % y, -x % -y, y % -y, -y % y

    f = epyccel(modulo_r_i, language=language)
    x = uniform(low=0, high=1e6)
    y = randint(low=1, high=1e6)


    f_output = f(x, y)
    modulo_r_i_output = modulo_r_i(x, y)
    assert allclose(f_output, modulo_r_i_output, rtol=RTOL, atol=ATOL)
    assert isinstance(f_output, type(modulo_r_i_output))

def test_modulo_int_real(language):
    def modulo_i_r(x : 'int', y : 'float'):
        return x % y, x % -y, -x % y, -x % -y, y % -y, -y % y

    f = epyccel(modulo_i_r, language=language)
    x = randint(0, 1e6)
    y = uniform(low=1, high=1e2)

    f_output = f(x, y)
    modulo_i_r_output = modulo_i_r(x, y)
    assert allclose(f_output, modulo_i_r_output, rtol=RTOL, atol=ATOL)
    assert isinstance(f_output, type(modulo_i_r_output))

def test_modulo_multiple(language):
    def modulo_multiple(x : 'int', y : 'float', z : 'int'):
        return x % y % z, -x % y % z, -x % -y % z, -x % -y % -z, \
               x % -y % z, x % -y % -z, x % y % -z, -x % y % -z, \
                   -y % y % y, y % -y % y, y % y % -y

    f = epyccel(modulo_multiple, language=language)
    x = randint(0, 1e6)
    y = uniform(low=1, high=1e4)
    z = randint(low=1, high=1e2)

    assert allclose(f(x, y, z), modulo_multiple(x, y, z), rtol=RTOL, atol=ATOL)
    assert isinstance(f(x, y, z), type(modulo_multiple(x, y, z)))
