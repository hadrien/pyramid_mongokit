# -*- coding: utf-8 -*-
import os


def setUpPackage():
    os.environ['MONGO_URI'] = 'mongodb://localhost/pyramid_mongokit'


def tearDownPackage():
    del os.environ['MONGO_URI']
