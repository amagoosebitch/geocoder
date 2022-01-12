class Prefixes:
    def __init__(self):
        self._city_prefixes = ['Гор', 'Г', 'Город']
        self._street_prefixes = ['Улица', 'Проспект', 'Бульвар', 'Аллея', 'Переулок', 'Тракт', 'Набережная', 'Линия',
                                 'Ул', 'Пр', 'Пр-кт', 'Б-р', 'Аллея', 'Пер', 'Тракт', 'Наб', 'Линия']
        self._building_prefixes = ['Дом', 'Д', 'Д.']
        self._building_postfixes = ['Строение', 'Корпус', 'Литера', 'Лит', 'Стр', 'Корп', 'К', 'Лит.', 'Стр.', 'Корп.',
                                    'К.']

        self._building_replacements = {'Строение': 'cтр.', 'C': 'стр.', 'Стр': 'стр.',
                                       'Корпус': 'к', 'Корп': 'к', 'К': 'к',
                                       'Литера': 'Лит', 'Л': 'Лит', 'Лит': 'Лит'}

        self._street_replacements = {'Улица': ['Ул'], 'Проспект': ['Пр', 'Пр-кт'], 'Бульвар': ['Б-р'], 'Аллея': [],
                                     'Переулок': ['Пер'], 'Тракт': [], 'Набережная': ['Наб'], 'Линия': []}

    @property
    def street_prefixes(self):
        return self._street_prefixes

    @property
    def building_prefixes(self):
        return self._building_prefixes

    @property
    def building_postfixes(self):
        return self._building_postfixes

    @property
    def building_replacements(self):
        return self._building_replacements

    @property
    def street_replacements(self):
        return self._street_replacements

    @property
    def city_prefixes(self):
        return self._city_prefixes
