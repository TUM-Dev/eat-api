# eat-api

[![Actions Status](https://github.com/TUM-Dev/eat-api/workflows/CI%2FCD/badge.svg)](https://github.com/TUM-Dev/eat-api/actions)


Simple static API for the canteens of the [Studierendenwerk München Oberbayern](http://www.studierendenwerk-muenchen-oberbayern.de) as well as some other canteens. By now, the following canteens are supported:

| Name                           | API-key                        | Address                                                                                                                     |
|:-------------------------------|:-------------------------------|:----------------------------------------------------------------------------------------------------------------------------|
| Mensa Arcisstraße              | mensa-arcisstr                 | [Arcisstraße 17, München](https://www.google.com/maps?q=Arcisstraße+17,+München)                                            |
| Mensa Garching                 | mensa-garching                 | [Boltzmannstraße 19, Garching](https://www.google.com/maps?q=Boltzmannstraße+19,+Garching)                                  |
| Mensa Leopoldstraße            | mensa-leopoldstr               | [Leopoldstraße 13a, München](https://www.google.com/maps?q=Leopoldstraße+13a,+München)                                      |
| Mensa Lothstraße               | mensa-lothstr                  | [Lothstraße 13d, München](https://www.google.com/maps?q=Lothstraße+13d,+München)                                            |
| Mensa Martinsried              | mensa-martinsried              | [Großhaderner Straße 6, Planegg-Martinsried](https://www.google.com/maps?q=Großhaderner%20Straße+6,+Planegg-Martinsried)    |
| Mensa Pasing                   | mensa-pasing                   | [Am Stadtpark 20, München](https://www.google.com/maps?q=Am%20Stadtpark+20,+München)                                        |
| Mensa Weihenstephan            | mensa-weihenstephan            | [Maximus-von-Imhof-Forum 5, Freising](https://www.google.com/maps?q=Maximus-von-Imhof-Forum+5,+Freising)                    |
| StuBistro Arcisstraße          | stubistro-arcisstr             | [Arcisstraße 12, München](https://www.google.com/maps?q=Arcisstraße+12,+München)                                            |
| StuBistro Goethestraße         | stubistro-goethestr            | [Goethestraße 70, München](https://www.google.com/maps?q=Goethestraße+70,+München)                                          |
| StuBistro Großhadern           | stubistro-großhadern           | [Butenandtstraße 13, Gebäude F, München](https://www.google.com/maps?q=Butenandtstraße+13,+Gebäude+F,+München)              |
| StuBistro Rosenheim            | stubistro-rosenheim            | [Hochschulstraße 1, Rosenheim](https://www.google.com/maps?q=Hochschulstraße+1,+Rosenheim)                                  |
| StuBistro Schellingstraße      | stubistro-schellingstr         | [Schellingstraße 3, München](https://www.google.com/maps?q=Schellingstraße+3,+München)                                      |
| StuBistro Martinsried          | stubistro-martinsried          | [Großhadernerstr. 9a, 82152 Planegg-Martinsried](https://www.google.com/maps/place/Gro%C3%9Fhaderner+Str.+9,+82152+Planegg) |
| StuCafé Adalbertstraße         | stucafe-adalbertstr            | [Adalbertstraße 5, München](https://www.google.com/maps?q=Adalbertstraße+5,+München)                                        |
| StuCafé Akademie Weihenstephan | stucafe-akademie-weihenstephan | [Alte Akademie 1, Freising](https://www.google.com/maps?q=Alte%20Akademie+1,+Freising)                                      |
| StuCafé Weihenstephan-Maximus  | stucafe-weihenstephan-maximus  | [Maximus-von-Imhof-Forum 5, 85354 Freising](https://www.google.com/maps/place/Maximus-von-Imhof-Forum+5,+85354+Freising)    |
| StuCafé Boltzmannstraße        | stucafe-boltzmannstr           | [Boltzmannstraße 15, Garching](https://www.google.com/maps?q=Boltzmannstraße+15,+Garching)                                  |
| StuCafé in der Mensa Garching  | stucafe-garching               | [Boltzmannstraße 19, Garching](https://www.google.com/maps?q=Boltzmannstraße+19,+Garching)                                  |
| StuCafé Karlstraße             | stucafe-karlstr                | [Karlstraße 6, München](https://www.google.com/maps?q=Karlstraße+6,+München)                                                |
| StuCafé Pasing                 | stucafe-pasing                 | [Am Stadtpark 20, München](https://www.google.com/maps?q=Am%20Stadtpark+20,+München)                                        |
| FMI Bistro Garching            | fmi-bistro                     | [Boltzmannstraße 3, Garching](https://www.google.com/maps?q=Boltzmannstraße+3,+Garching)                                    |
| IPP Bistro Garching            | ipp-bistro                     | [Boltzmannstraße 2, Garching](https://goo.gl/maps/vYdsQhgxFvH2)                                                             |
| Mensa Bildungscampus Heilbronn | mensa-bildungscampus-heilbronn | [Bildungscampus 8, Heilbronn](https://maps.app.goo.gl/Jq2p9fKkjTMPrvd39)                                                    |

## Label list - previously _ingredients_:
See [here](https://tum-dev.github.io/eat-api/enums/labels.json).

## Usage

### API

The actual API is provided by static JSON files, which can be found in the gh-pages branch of this repository. These files are created through automatic travis builds. 
The documentation can be found at: https://tum-dev.github.io/eat-api/docs

Basically, you need to structure a link as follows in order to access the API:

```
https://tum-dev.github.io/eat-api/<canteen>/<year>/<week-number>.json
```

#### Example

The following link would give you the menu of Mensa Garching for week 20 in 2019:

```
https://tum-dev.github.io/eat-api/mensa-garching/2019/20.json
```

### CLI

The JSON files are produced by the tool shown in this repository. Hence, it is either possible to access the API or use the tool itself to obtain the desired menu data. The CLI needs to be used as follows:

```bash
$ src/python3 main.py --help
usage: main.py [-h] [-p CANTEEN] [-d DATE] [-j PATH] [-c] [--openmensa PATH]
               [--canteens] [--language LANGUAGE]

options:
  -h, --help            show this help message and exit
  -p CANTEEN, --parse CANTEEN
                        the canteen you want to eat at
  -d DATE, --date DATE  date (DD.MM.YYYY) of the day of which you want to get
                        the menu
  -c, --combine         creates a "combined.json" file containing all dishes
                        for the canteen specified
  --openmensa PATH      directory for OpenMensa XML output (date parameter
                        will be ignored if this argument is used)
  --canteens            prints all available canteens formated as JSON
  --language LANGUAGE   The language to translate the dish titles to, needs an
                        DeepL API-Key in the environment variable
                        DEEPL_API_KEY_EAT_API

```

It is mandatory to specify the canteen (e.g. mensa-garching). Furthermore, you can specify a date, for which you would like to get the menu. If no date is provided, all the dishes for the current week will be printed to the command line. the `--jsonify` option is used for the API and produces some JSON files containing the menu data.

#### Example

Here are some sample calls:

```
# Get the menus for the whole current week at mensa-garching
$ python src/main.py -p mensa-garching

# Get the menu for April 2 at mensa-arcisstrasse
$ python src/main.py -p mensa-arcisstrasse -d 02.04.2019
```

#### Translations

Dish titles are provided only in german by the Studentenwerk. 
We offer the possibility to translate them using the DeepL API.
In order to use the API, there needs to be an API key provided in the environment variable `DEEPL_API_KEY_EAT_API`.
The target language can be specified using the `--language` option using one of the languages supported by DeepL e.g. `EN-US`.

### Generating `canteens.json` and `label.json`

The `canteens.json` and `label.json` are generated from the `Canteen` and `Label` enum. To generate them, run `enum_json_creator.py [<path/to/directory>]`. This will also generate a `languages.json` file, which contains the languages supported by the `Label` enum. If no path is specified, the Python script stores them in `./dist/enums`.

## Projects using `eat-api`

-   Parser for [OpenMensa](https://openmensa.org) ([GitHub](https://github.com/openmensa/openmensa))
    -   [Wilhelm Gastronomie im FMI Gebäude der TUM Garching](https://openmensa.org/c/773)
    -   [Konradhofer Catering - Betriebskantine IPP](https://openmensa.org/c/774)
-   [Hunger | TUM.sexy](http://tum.sexy/hunger/) ([Github](https://github.com/mammuth/TUM.sexy))
-   `FMeat.php` SDK ([GitHub](https://github.com/jpbernius/fmeat.php))
-   [Telegram](https://telegram.org/) bot for [Channel t.me/lunchgfz](https://t.me/lunchgfz) ([GitLab](https://gitlab.com/raabf/lunchgfz-telegram))
-   UWP-TUM-Campus-App ([Github](https://github.com/COM8/UWP-TUM-Campus-App))

## Contributing

### Getting started

1. Fork and clone this repository
2. Install the python dependencies (Python 3.9+ required):

-   `sudo apt install libxml2 libxml2-dev libxslt1-dev`
-   `pip3 install poetry`
-   `poetry install`

### pre-commit

Code quality is ensured via various tools bundled in [`pre-commit`](https://github.com/pre-commit/pre-commit/).

You can install `pre-commit`, so it will automatically run on every commit:

```bash
pre-commit install
```

This will check all files modified by your commit and will prevent the commit if a hook fails. To check all files, you can run

```bash
pre-commit run --all-files
```

This will also be run by CI if you push to the repository.

### Run tests:

-   All the tests: `PYTHONPATH=src/ pytest`
-   A specific test class: `PYTHONPATH=src/ pytest src/test/test_menu_parser.py::MenuParserTest`
