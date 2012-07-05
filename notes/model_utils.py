#!/usr/bin/python
# -*- coding:utf8 -*-
""" Utilities for model classes. Separate namespace here to avoid circular imports
"""
from random import choice
import string

def fast_hash(letters=6):
    """ Generates a unique pseudo-random identifier of hex values.
        Used for invite codes on user_profiles
    """
    return ''.join([choice(string.hexdigits) for n in xrange(letters)])
