import math

from constants import MINOR_AXIS_RATIO


def throat_diameter(wt_diameter, clearance):
    return wt_diameter + 2 * clearance


def chord_length(dth, c_dth):
    return c_dth * dth


def minor_axis(chord):
    return MINOR_AXIS_RATIO * chord


def shell_diameter(dth, b):
    return dth + 2 * b


def cross_section_area(chord, b):
    return math.pi * (chord / 2) * (b / 2)


def shell_volume(area, dth, dsh):
    return math.pi * area * ((dth + dsh) / 2)


def ellipse_h(chord, b):
    return ((chord / 2 - b / 2) ** 2) / ((chord / 2 + b / 2) ** 2)


def ellipse_perimeter(chord, b):
    h = ellipse_h(chord, b)

    return math.pi * ((b + chord) / 2) * (
        1 + (3 * h) / (10 + math.sqrt(4 - 3 * h))
    )


def shroud_surface_area(perimeter, dth, dsh):
    return perimeter * ((dth + dsh) / 2) * math.pi