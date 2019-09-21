# -*- coding: utf-8 -*-

# $Id:$


def constraint_to_range(value, min_, max_):
    if value < min_:
        return min_
    if value > max_:
        return max_
    return value
