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
        prefixes_class = Prefixes()
        result = []
        for part in parts:
            for inner_part in re.split(r',', part):
                if len(inner_part) != 0:
                    splitted = [splitted_part.lower().title() for splitted_part in inner_part.replace('.', ' ').split()]
                    if any(splitted_part in prefixes_class.all_prefixes() for splitted_part in splitted):
                        result += splitted
                    else:
                        result.append(inner_part.lower().title())
        return result

    def _set_city(self, city):
        splitted_city = city.split()
        args_to_remove = splitted_city.copy()
        index = self.dynamic_info.index(args_to_remove[0])
        if index > 0 and self.dynamic_info[index - 1].lower().title() in self.prefixes_class.city_prefixes:
            args_to_remove.append(self.dynamic_info[index - 1])
        for arg in args_to_remove:
            self.dynamic_info.remove(arg)
        self.city = ' '.join(splitted_city)

    def _find_city(self):
        conn = sqlite3.connect(Path(__file__).parent.parent / Path('db') / 'cities.db')
        cursor = conn.cursor()
        cities = set(cursor.execute('SELECT city FROM cities').fetchall())
        cities = [x[0] for x in cities]
        args = self.make_pairs_and_triples(self.info)
        for value in args:
            found_value, possible_city = self.try_find_city_from_word(cities, value, cursor)
            if found_value:
                return found_value, possible_city
        city = self._find_city_with_mistakes(cities)
        if city:
            return self.extract_city_data(cursor, city)
        print('Такого города нет в базе данных городов России.')
        sys.exit(-1)

    def extract_city_data(self, cursor, city):
        cursor.execute(f'SELECT * FROM cities WHERE city="{city}"')
        found_value = cursor.fetchone()
        self._set_city(city)
        return found_value, city

    def _find_city_with_mistakes(self, cities):
        args = self.make_pairs_and_triples(self.dynamic_info)
        for arg in args:
            if arg in self.prefixes_class.city_prefixes:
                args = args[args.index(arg) + 1: args.index(arg) + 2]
                self.dynamic_info.remove(arg)
                break
        possible_cities_info = set()
        for arg in args:
            self.find_possible_cities(cities, possible_cities_info, arg)
        possible_cities_info = list(possible_cities_info)
        possible_cities_info.sort(key=lambda x: x[1], reverse=True)
        temp = set()
        for possible_city_info in possible_cities_info.copy()[:6]:
            if possible_city_info[0] in temp:
                possible_cities_info.remove(possible_city_info)
            else:
                temp.add(possible_city_info[0])
        return self.handle_city_choice(possible_cities_info[:3])

    def handle_city_choice(self, possible_cities_info):
        if len(possible_cities_info) > 1:
            string = '\n'
            for num, word in enumerate(possible_cities_info):
                string += '{}: {}\n'.format(num+1, word[0])
            while True:
                answer = input(f'Введите номер города, который вы имели в виду: {string}')
                if answer.isdigit() and int(answer) <= len(possible_cities_info):
                    break
                else:
                    print('Неверный формат ввода.')
            city = possible_cities_info[int(answer)-1]
            splitted_inputted_city = city[2].split()
            splitted_actual_city = city[0].split()
            for part in splitted_inputted_city:
                self.dynamic_info.remove(part)
                self.info.remove(part)
            for part in splitted_actual_city:
                self.dynamic_info.append(part)
                self.info.append(part)
            return city[0]
        if len(possible_cities_info) == 1:
            city = possible_cities_info[0]
            self.dynamic_info[self.dynamic_info.index(city[2])] = city[0]
            self.info[self.info.index(city[2])] = city[0]
            return city[0]
        return None

    @staticmethod
    def find_possible_cities(cities, possible_cities_info, arg):
        best_matches = process.extractBests(arg, cities, limit=3)
        for possible_city, coef in best_matches:
            if coef >= 70:
                possible_cities_info.add((possible_city, coef, arg))

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
        self.dynamic_info.remove(building)
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
                    return self._handle_building_deletion_info(possible_building)
            else:
                next_element = self.info[index+1]
                if next_element == self.city or any(map(str.isdigit, next_element)):
                    return self._handle_building_deletion_info(possible_building)
        return self._handle_building_deletion_info(possible_buildings[0])

    def _find_street(self):
        if len(self.dynamic_info) == 0:
            print('Неверный формат данных')
            sys.exit(-2)
        part = self.dynamic_info[0]
        if part.lower().title() in self.prefixes_class.street_prefixes:
            self.street_type = part.lower().title()
            self.dynamic_info.remove(part)

        street = ' '.join(self.dynamic_info)
        self.street = street
        return street

    def parse(self):
        city_info, city = self.pre_handle_parsing()
        if not self.city:
            city_info, city = self._find_city()
        if not self.building:
            building = self._find_building()
        else:
            building = self.building
        street = self._find_street()
        return city_info, city, street, self.street_type, building

    def pre_handle_parsing(self):
        parts = self.string_to_parse.split(',')
        if len(parts) == 1:
            return None, None
        possible_cities_info = set()
        cursor, cities = self.create_cities_and_cursor()
        for part in parts:
            part = part.strip()
            if len(part) == 0:
                continue
            found_value, city = self.try_find_city_from_word(cities, part, cursor)
            if found_value:
                return found_value, city
            elif len(part.split()) != 1:
                args = self.make_pairs_and_triples(part.split())
                for arg in args:
                    found_value, city = self.try_find_city_from_word(cities, arg, cursor)
                    if found_value:
                        return found_value, city
            else:
                self.find_possible_cities(cities, possible_cities_info, part)
        possible_cities_info = list(possible_cities_info)
        possible_cities_info.sort(key=lambda x: x[1], reverse=True)
        city = self.handle_city_choice(possible_cities_info)
        return self.extract_city_data(cursor, city)

    def try_find_city_from_word(self, cities, word, cursor):
        if word in cities:
            cursor.execute(f'SELECT * FROM cities WHERE city="{word}"')
            found_value = cursor.fetchone()
            if found_value:
                self._set_city(word)
                return found_value, word
        else:
            return None, None

    @staticmethod
    def create_cities_and_cursor():
        conn = sqlite3.connect(Path(__file__).parent.parent / Path('db') / 'cities.db')
        cursor = conn.cursor()
        cities = set(cursor.execute('SELECT city FROM cities').fetchall())
        return cursor, [x[0] for x in cities]

    @staticmethod
    def make_pairs_and_triples(args):
        return args + [' '.join(args[i:i+2]) for i in range(len(args)-1)] + [' '.join(args[i:i+3]) for i in range(len(args)-2)]