#!/bin/bash

yum install -y swig libftdi-devel

/opt/python/cp27-cp27mu/bin/pip wheel /io/ -w /io/wheelhouse/

auditwheel repair /io/wheelhouse/libmpsse*.whl -w /io/wheelhouse/
