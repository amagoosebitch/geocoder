import argparse
from src import input_parser
from itertools import permutations
import os
import pytest


def pattern_for_tests(args):
    parser = input_parser.InputParser(args, ' '.join(args))
    city_info, actual_city = parser.find_city(args)
    actual_building = parser.find_building()
    actual_street = parser.find_street()
    return actual_city, actual_street, actual_building


def test_simple_parse():
    args = ['Екатеринбург', 'чапаева', '16']
    for permutation in permutations(args):
        actual_city, actual_street, actual_building = pattern_for_tests(list(permutation))
        assert actual_city == 'Екатеринбург'
        assert actual_street == 'Чапаева'
        assert actual_building == '16'


def test_building_with_char():
    args = ['Екатеринбург', 'Чапаева', '16А']
    for permutation in permutations(args):
        actual_city, actual_street, actual_building = pattern_for_tests(list(permutation))
        assert actual_city == 'Екатеринбург'
        assert actual_street == 'Чапаева'
        assert actual_building == '16А'


def test_city_in_input():
    args = ['город', 'Екатеринбург', 'Чапаева', '16А']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Екатеринбург'
    assert actual_street == 'Чапаева'
    assert actual_building == '16А'


def test_street_in_input():
    args = ['Екатеринбург', 'улица', 'Чапаева', '16А']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Екатеринбург'
    assert actual_street == 'Чапаева'
    assert actual_building == '16А'


def test_building_in_input():
    args = ['Екатеринбург', 'Чапаева', 'дом', '16А']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Екатеринбург'
    assert actual_street == 'Чапаева'
    assert actual_building == '16А'


def test_city_street_building_in_input():
    args = ['город', 'Екатеринбург', 'улица', 'Чапаева', 'дом', '16А']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Екатеринбург'
    assert actual_street == 'Чапаева'
    assert actual_building == '16А'


def test_abbreviated():
    args = ['город', 'Екатеринбург', 'ул.Чапаева', 'дом', '16А']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Екатеринбург'
    assert actual_street == 'Чапаева'
    assert actual_building == '16А'


def test_some_weird_registers_in_input():
    args = ['гоРод', 'екаТеринбург', 'Улица', 'чаПАева', 'дОм', '16А']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Екатеринбург'
    assert actual_street == 'Чапаева'
    assert actual_building == '16А'


def test_several_parted_street():
    args = ['город', 'Волжский', '40', 'лет', 'Победы', '5']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Волжский'
    assert actual_street == '40 Лет Победы'
    assert actual_building == '5'


def test_several_parted_and_abbreviated():
    args = ['город', 'Волжский', 'ул', '40', 'лет', 'Победы', '5']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Волжский'
    assert actual_street == '40 Лет Победы'
    assert actual_building == '5'


def test_street_without_space():
    args = ['город', 'Волжский', 'ул.40', 'лет', 'Победы', '5']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Волжский'
    assert actual_street == '40 Лет Победы'
    assert actual_building == '5'