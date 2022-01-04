# Geocoder
Версия 0.1

Авторы: [Полуяненко Алёна](https://github.com/NiripsaKakVsegda), [Лифанов Фёдор](https://github.com/amagoosebitch)

Ревью выполнил: [Александр Анкудинов](https://github.com/xelez)
# Описание
Данный скрипт позволяет получить полный адрес и его координаты по свободному вводу адреса (можно менять местами город, улицу и здание, 
использовать "г., гор., ул.", допускаются опечатки). Работает только в России. Некоторые города и адреса отсутствуют в связи с отсутствием
данных в Overpass-de (OpenStreetMap). 
# Требования
* Python 3.8 и выше
* установка `requirements.txt`
* установка MongoDB (записать путь к файлу mongod.exe в файл `config/config.txt`)
    * https://www.mongodb.com/try/download/community (установить complete версию)
* установка русского словаря pyenchant  
>Файлы словаря "ru_RU.dic" и "ru_RU.aff" можно взять из офисных пакетов openoffice и libreoffice.
>Их необходимо скопировать в папку 

`..Python36/Lib/site-packages/enchant/share/enchant/myspell`
# Состав
* `config`: папка. где хранится конфигурационный файл с путем до mongod.exe

* `src\cities_db_maker.py`: скрипт по созданию базы данных городов (создает файл `cities.db`)

* `src\main.py`: основной скрипт

* `src\xml_parser`: скрипт по преобразованию xml файла города в MongoDB

* `src\tools` : набор функций, необходимый для работы программы

* `src\input_parser.py`: набо функций, отвечающий за парсинг ввода
# Работа скрипта
```
python src\main.py -g [адрес в свободной форме]
```
# TODO
* парсить разный ввод адресов (с точками\запятыми, гор., ул. и т.д.)
* парсить корявые адреса (с опечатками)
* странные адреса из статьи
* докер (?)