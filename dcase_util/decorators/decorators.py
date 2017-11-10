# !/usr/bin/env python
# -*- coding: utf-8 -*-


class RunOnce(object):
    """Decorator class to allow only one execution"""
    def __init__(self, f):
        self.f = f
        self.function_ran = False

    def __call__(self, *args, **kwargs):
        if not self.function_ran:
            self.function_ran = True
            return self.f(*args, **kwargs)
