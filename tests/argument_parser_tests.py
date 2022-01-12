import argparse
from src import input_parser
from itertools import permutations
import os
import pytest


def pattern_for_tests(args):
    parser = input_parser.InputParser(args, ' '.join(args))
    city_info, actual_city, actual_street, street_type, actual_building = parser.parse()
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


def test_city_in_input():  # для других префиксов
    args = ['город', 'Екатеринбург', 'Чапаева', '16А']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Екатеринбург'
    assert actual_street == 'Чапаева'
    assert actual_building == '16А'


def test_street_in_input():  # для других префиксов
    args = ['Екатеринбург', 'улица', 'Чапаева', '16А']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Екатеринбург'
    assert actual_street == 'Чапаева'
    assert actual_building == '16А'


def test_building_in_input():  # для других префиксов
    args = ['Екатеринбург', 'Чапаева', 'дом', '16А']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Екатеринбург'
    assert actual_street == 'Чапаева'
    assert actual_building == '16А'


def test_city_street_building_in_input():
    args = ['город', 'Екатеринбург', 'ул.', 'Чапаева', 'д', '16А']
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


def test_nonexistent_city():
    args = ['idc', 'sheeesh', '40']
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        actual_city, actual_street, actual_building = pattern_for_tests(args)
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == -1


def test_litera():
    args = ['Санкт-Петербург', 'проспект', 'Обуховской', 'Обороны', '106', 'лит.В']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Санкт-Петербург'
    assert actual_street == 'Обуховской Обороны'
    assert actual_building == '106 ЛитВ'


def test_korpus():
    args = ['Санкт-Петербург', 'Савушкина', '83', 'корпус', '3']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Санкт-Петербург'
    assert actual_street == 'Савушкина'
    assert actual_building == '83 к3'


def test_very_bad_input():
    args = ['Кораблестроителей', 'Санкт-Петербург', 'дом', '35', 'корпус', '1', 'литера', 'В']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Санкт-Петербург'
    assert actual_street == 'Кораблестроителей'
    assert actual_building == '35 к1 ЛитВ'


def test_mistakes_in_city():
    args = ['город', 'Екатеиньург', 'ул.Тургенева', 'дом', '16А']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Екатеринбург'
    assert actual_street == 'Тургенева'
    assert actual_building == '16А'


def test_multiple_choice(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "1")
    args = ['город', 'Екатеиньург', 'Чапаева', 'дом', '16А']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Екатеринбург'
    assert actual_street == 'Чапаева'
    assert actual_building == '16А'


def test_multiple_choice_when_street_is_first(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "2")
    args = ['Ектаеиньуг', 'Чапаева', 'дом', '16А']
    actual_city, actual_street, actual_building = pattern_for_tests(args)
    assert actual_city == 'Екатеринбург'
    assert actual_street == 'Чапаева'
    assert actual_building == '16А'