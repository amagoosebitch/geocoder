from tools import *


class InputParser:
    def __init__(self, values, string_to_parse):
        self.string_to_parse = string_to_parse
        self.info = values.copy()
        self.dynamic_info = values.copy()
        self.city = ''
        self.street = ''
        self.building = ''

    def set_city(self, city):
        self.dynamic_info.remove(city)
        self.city = city

    @staticmethod
    def find_city(values):
        conn = sqlite3.connect(os.path.join(Path(__file__).parent.parent, r'db\cities.db'))
        cursor = conn.cursor()
        for value in values:
            value = value.lower().title()
            cursor.execute(f'SELECT * FROM cities WHERE city="{value}"')
            found_value = cursor.fetchone()
            if found_value:
                return found_value, value
        print('Такого города нет в базе данных городов России.')
        sys.exit(-1)

    def find_building(self):
        address = self.dynamic_info
        regex = re.compile(r'(\d{1,4})(\w{0,4})$')
        possible_buildings = []
        for value in address:
            match = re.match(regex, value)
            if match:
                possible_buildings.append(value)
        builing = self.choose_building(possible_buildings)
        self.dynamic_info.remove(builing)
        return builing

    def choose_building(self, possible_buildings):
        possible_prefixes = ['Улица', 'Проспект', 'Бульвар', 'Аллея', 'Переулок', 'Тракт', 'Набережная', 'Линия']
        for possible_building in possible_buildings:
            index = self.info.index(possible_building)
            if index > 0:
                previous_element = self.info[index-1].lower().title()
                if previous_element != self.city and previous_element not in possible_buildings \
                        and previous_element not in possible_prefixes:
                    return possible_building
            else:
                next_element = self.info[index+1]
                if next_element == self.city or any(map(str.isdigit, next_element)):
                    return possible_building
        return possible_buildings[0]

    def find_street(self):
        return ' '.join(self.dynamic_info)