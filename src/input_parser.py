from src.tools import *
from src.prefixes_class import Prefixes
from pathlib import Path


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
            for inner_part in part.split('.'):
                result.append(inner_part.lower().title())
        return result

    def set_city(self, city):
        args_to_remove = [city]
        index = self.dynamic_info.index(city)
        if self.dynamic_info[index - 1].lower().title() == 'Город':
            args_to_remove.append(self.dynamic_info[index - 1])
        for arg in args_to_remove:
            self.dynamic_info.remove(arg)
        self.city = city

    def find_city(self, values):
        conn = sqlite3.connect(Path(__file__).parent.parent / Path('db') / 'cities.db')
        cursor = conn.cursor()
        for value in values:
            value = value.lower().title()
            cursor.execute(f'SELECT * FROM cities WHERE city="{value}"')
            found_value = cursor.fetchone()
            if found_value:
                self.set_city(value)
                return found_value, value
        print('Такого города нет в базе данных городов России.')
        sys.exit(-1)

    def find_building(self):
        address = self.dynamic_info
        regex = re.compile(r'(\d{1,4})(\\|/|\s|-)?(\d{0,4})(\w{0,4})$')
        possible_buildings = []
        for value in address:
            match = re.search(regex, value)
            if match:
                possible_buildings.append(value)
        building = self.choose_building(possible_buildings)
        return building

    def handle_building_deletion_info(self, building):
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
                if current_word in self.prefixes_class.replacements.keys():
                    result += ' ' + self.prefixes_class.replacements[current_word]
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

    def choose_building(self, possible_buildings):
        street_prefixes = self.prefixes_class.street_prefixes
        for possible_building in possible_buildings:
            index = self.info.index(possible_building)
            if index > 0:
                previous_element = self.info[index-1].lower().title()
                if previous_element != self.city and previous_element not in possible_buildings \
                        and previous_element not in street_prefixes:
                    self.dynamic_info.remove(possible_building)
                    return self.handle_building_deletion_info(possible_building)
            else:
                next_element = self.info[index+1]
                if next_element == self.city or any(map(str.isdigit, next_element)):
                    self.dynamic_info.remove(possible_building)
                    return self.handle_building_deletion_info(possible_building)
        self.dynamic_info.remove(possible_buildings[0])
        return possible_buildings[0]

    def find_street(self):
        for part in self.dynamic_info.copy():
            if part.lower().title() in self.prefixes_class.street_prefixes:
                self.street_type = part
                self.dynamic_info.remove(part)

        return ' '.join(self.dynamic_info)