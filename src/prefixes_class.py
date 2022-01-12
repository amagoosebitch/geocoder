class Prefixes:
    def __init__(self):
        self._city_prefixes = ['Гор', 'Г', 'Город']
        self._street_prefixes = ['Улица', 'Проспект', 'Бульвар', 'Аллея', 'Переулок', 'Тракт', 'Набережная', 'Линия',
                                 'Ул', 'Пр', 'Пр-кт', 'Б-р', 'Аллея', 'Пер', 'Тракт', 'Наб', 'Линия',
                                 'Ул.', 'Пр.', 'Пр-кт.', 'Б-р.', 'Пер.', 'Наб.']
        self._building_prefixes = ['Дом', 'Д', 'Д.']
        self._building_postfixes = ['Строение', 'Корпус', 'Литера', 'Лит', 'Стр', 'Корп', 'К', 'Лит.', 'Стр.', 'Корп.',
                                    'К.']

        self._replacements = {'Строение': 'cтр.', 'Корпус': 'к', 'Литера': 'лит'}

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
    def replacements(self):
        return self._replacements

    @property
    def city_prefixes(self):
        return self._city_prefixes
