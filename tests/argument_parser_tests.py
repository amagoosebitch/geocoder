import argparse
from src.input_parser import InputParser
from itertools import permutations
import os
import pytest


def pattern_for_tests(args):
    input_parser = InputParser(args, ' '.join(args))
    city_info, actual_city = input_parser.find_city(args)
    input_parser.set_city(actual_city)
    actual_building = input_parser.find_building()
    actual_street = input_parser.find_street()
    return actual_city, actual_street, actual_building


def test_simple_parse():
    args = ['Екатеринбург', 'Чапаева', '16']
    for permutation in permutations(args):
        actual_city, actual_street, actual_building = pattern_for_tests(list(permutation))
        assert actual_city == 'Екатеринбург'
        assert actual_street == 'Чапаева'
        assert actual_building == '16'


def test_building_with_char():
    args = ['Екатеринбург', 'Чапаева', '16A']
    for permutation in permutations(args):
        actual_city, actual_street, actual_building = pattern_for_tests(list(permutation))
        assert actual_city == 'Екатеринбург'
        assert actual_street == 'Чапаева'
        assert actual_building == '16A'