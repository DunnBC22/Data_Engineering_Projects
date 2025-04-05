# Beverage Sales - Apache NiFi Pipeline

This project retrieves data from Elasticsearch, makes transformations and then sends them to a MySQL table. Apache NiFi, Elasticsearch, and MySQL are all in their own docker containers.

I have included the Flow Definition Files (both with and without exernal services).

## Notes

- Handle Discrete Values for the following features according to the charts listed here:
    - Customer_Type
        - 'B2C' -> 0
        - 'B2B' -> 1
        - (any others) -> -1
    - Product
        - 'Warsteiner' -> 0
        - 'Apollinaris' -> 1
        - 'Evian' -> 2
        - 'Rauch Multivitamin' -> 3
        - 'Mountain Dew' -> 4
        - 'Vio Wasser' -> 5
        - 'Kölsch' -> 6
        - 'Granini Apple' -> 7
        - 'Monster' -> 8
        - 'Rockstar' -> 9
        - 'Rotkäppchen Sekt' -> 10
        - 'Merlot' -> 11
        - 'Selters' -> 12
        - 'Volvic Touch' -> 13
        - 'Erdinger Weißbier' -> 14
        - 'Mezzo Mix' -> 15
        - 'Havana Club' -> 16
        - 'Krombacher' -> 17
        - 'Red Bull' -> 18
        - 'Passion Fruit Juice' -> 19
        - 'Bacardi' -> 20
        - 'Sprite' -> 21
        - 'Pepsi' -> 22
        - 'San Pellegrino' -> 23
        - 'Fanta' -> 24
        - 'Johnnie Walker' -> 25
        - 'Riesling' -> 26
        - 'Beck's' -> 27
        - 'Chardonnay' -> 28
        - 'Sauvignon Blanc' -> 29
        - 'Volvic' -> 30
        - 'Mango Juice' -> 31
        - 'Gerolsteiner' -> 32
        - 'Tanqueray' -> 33
        - 'Club Mate' -> 34
        - 'Cranberry Juice' -> 35
        - 'Hohes C Orange' -> 36
        - 'Jack Daniels' -> 37
        - 'Vittel' -> 38
        - 'Fritz-Kola' -> 39
        - 'Veuve Clicquot' -> 40
        - 'Jever' -> 41
        - 'Moët & Chandon' -> 42
        - 'Tomato Juice' -> 43
        - 'Schwip Schwap' -> 44
        - 'Augustiner' -> 45
        - 'Coca-Cola' -> 46
        - (any others) -> -1
    - Category
        - 'Alcoholic Beverages' -> 0
        - 'Water' -> 1
        - 'Soft Drinks' -> 2
        - 'Juices' -> 3
        - (any others) -> -1
    - Region
        - 'Nordrhein-Westfalen' -> 0
        - 'Bayern' -> 1
        - 'Baden-Württemberg' -> 2
        - 'Hamburg' -> 3
        - 'Niedersachsen' -> 4
        - 'Bremen' -> 5
        - 'Berlin' -> 6
        - 'Thüringen' -> 7
        - 'Brandenburg' -> 8
        - 'Schleswig-Holstein' -> 9
        - 'Mecklenburg-Vorpommern' -> 10
        - 'Sachsen' -> 11
        - 'Rheinland-Pfalz' -> 12
        - 'Hessen' -> 13
        - 'Sachsen-Anhalt' -> 14
        - 'Saarland' -> 15
        - (any others) -> -1
- Add a Unique ID feature
- Remove leading and trailing whitespace from features of String data type
- Handle Date Data type & extract date parts for Order_Date
- There are NO null values that I have to handle.
- Rename Columns

## Dataset Source
https://www.kaggle.com/datasets/sebastianwillmann/beverage-sales