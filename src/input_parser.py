from src.tools import *
from src.prefixes_class import Prefixes
from pathlib import Path
from fuzzywuzzy import process
import re


class InputParser:
    def __init__(self, values, string_to_parse):
        self.string_to_parse = string_to_parse
        self.info = InputParser.normalize_parts(values)
        self.dynamic_info = InputParser.normalize_parts(values)
        self.city = ''
        self.street = ''
        self.building = ''
        self.street_type = ''
        self.prefixes_class = Prefixes()

    @staticmethod
    def normalize_parts(parts):
        result = []
        for part in parts:
            for inner_part in re.split(r',|\.', part):
                if len(inner_part) != 0:
                    result.append(inner_part.lower().title())
        return result

    def _set_city(self, city):
        args_to_remove = [city]
        index = self.dynamic_info.index(city)
        if self.dynamic_info[index - 1].lower().title() in self.prefixes_class.city_prefixes:
            args_to_remove.append(self.dynamic_info[index - 1])
        for arg in args_to_remove:
            self.dynamic_info.remove(arg)
        self.city = city

    def _find_city(self):
        conn = sqlite3.connect(Path(__file__).parent.parent / Path('db') / 'cities.db')
        cursor = conn.cursor()
        cities = set(cursor.execute('SELECT city FROM cities').fetchall())
        cities = [x[0] for x in cities]
        for value in self.info:
            if value not in cities:
                continue
            cursor.execute(f'SELECT * FROM cities WHERE city="{value}"')
            found_value = cursor.fetchone()
            if found_value:
                self._set_city(value)
                return found_value, value

        city = self._find_city_with_mistakes(cities)
        if city:
            cursor.execute(f'SELECT * FROM cities WHERE city="{city}"')
            found_value = cursor.fetchone()
            self._set_city(city)
            return found_value, city
        print('Такого города нет в базе данных городов России.')
        sys.exit(-1)

    def _find_city_with_mistakes(self, cities):
        args = self.dynamic_info.copy()
        for arg in args:
            if arg in self.prefixes_class.city_prefixes:
                args = [args[args.index(arg) + 1]]
                self.dynamic_info.remove(arg)
                break
        possible_cities = []
        for arg in args:
            possible_city, coef = process.extractOne(arg, cities)
            if coef >= 70:
                possible_cities.append((possible_city, coef, arg))
        possible_cities.sort(key=lambda x: x[1], reverse=True)
        if len(possible_cities) > 1:
            string = '\n'
            for num, word in enumerate(possible_cities):
                string += '{}: {}\n'.format(num+1, word[0])
            while True:
                answer = input(f'Введите номер города, который вы имели в виду: {string}')
                if answer.isdigit() and int(answer) <= len(possible_cities):
                    break
                else:
                    print('Неверный формат ввода.')
            city = possible_cities[int(answer)-1]
            self.dynamic_info[self.dynamic_info.index(city[2])] = city[0]
            self.info[self.info.index(city[2])] = city[0]
            return city[0]
        if len(possible_cities) == 1:
            city = possible_cities[0]
            self.dynamic_info[self.dynamic_info.index(city[2])] = city[0]
            self.info[self.info.index(city[2])] = city[0]
            return city[0]
        return None

    def _find_building(self):
        address = self.dynamic_info
        regex = re.compile(r'(\d{1,4})(\\|/|\s|-)?(\d{0,4})(\w{0,4})$')
        possible_buildings = []
        for value in address:
            match = re.search(regex, value)
            if match:
                possible_buildings.append(value)
        building = self._choose_building(possible_buildings)
        self.building = building
        return building

    def _handle_building_deletion_info(self, building):
        result = ''
        info = self.info.copy()
        index = info.index(building)
        splitted_building_string = ''
        if info[index-1].lower().title() in self.prefixes_class.building_prefixes:
            self.dynamic_info.remove(info[index-1])
        for part in building.split('.'):
            if part.lower().title() not in self.prefixes_class.building_prefixes:
                splitted_building_string += part
        result += splitted_building_string
        for i in range(index+1, len(info)):
            current_word = info[i].lower().title()
            if current_word in self.prefixes_class.building_postfixes:
                self.dynamic_info.remove(info[i])
                if current_word in self.prefixes_class.building_replacements.keys():
                    result += ' ' + self.prefixes_class.building_replacements[current_word]
                else:
                    result += ' ' + info[i].replace('.', '')
                if info[i+1].isdigit():
                    result += info[i+1]
                    self.dynamic_info.remove(info[i+1])
                    i += 1
                elif current_word == 'Литера' or current_word == 'Лит':
                    self.dynamic_info.remove(info[i + 1])
                    result += info[i+1]
                    i += 1

        return result

    def _choose_building(self, possible_buildings):
        street_prefixes = self.prefixes_class.street_prefixes
        for possible_building in possible_buildings:
            index = self.info.index(possible_building)
            if index > 0:
                previous_element = self.info[index-1].lower().title()
                if previous_element != self.city and previous_element not in possible_buildings \
                        and previous_element not in street_prefixes:
                    self.dynamic_info.remove(possible_building)
                    return self._handle_building_deletion_info(possible_building)
            else:
                next_element = self.info[index+1]
                if next_element == self.city or any(map(str.isdigit, next_element)):
                    self.dynamic_info.remove(possible_building)
                    return self._handle_building_deletion_info(possible_building)
        self.dynamic_info.remove(possible_buildings[0])
        return possible_buildings[0]

    def _find_street(self):
        for part in self.dynamic_info.copy():
            if part.lower().title() in self.prefixes_class.street_prefixes:
                self.street_type = part
                self.dynamic_info.remove(part)

        street = ' '.join(self.dynamic_info)
        self.street = street
        return street

    def parse(self):
        city_info, city = self._find_city()
        if not self.building:
            building = self._find_building()
        else:
            building = self.building
        street = self._find_street()
        return city_info, city, street, self.street_type, building
