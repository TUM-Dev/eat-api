"""Regression coverage for current menu sources; all network responses are mocked."""

import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests
from lxml import html

from entities import Canteen, Label
from main import get_menu_parsing_strategy
from menu_parser import FMIBistroMenuParser, ParsingError, StudentenwerkMenuParser

ASSETS = Path(__file__).parent / "assets" / "studentenwerk" / "current"
CANTEENS = [
    (Canteen.MENSA_MARTINSRIED, 412, 11, "Pasta mit mediterraner Tomatensauce"),
    (Canteen.MENSA_PASING, 432, 6, "Schweizer Knöpflepfanne mit feinem Gemüse und Käse"),
    (Canteen.STUCAFE_ADALBERTSTR, 452, 4, "Pasta mit Gemüsebolognese"),
    (Canteen.STUCAFE_AKADEMIE_WEIHENSTEPHAN, 456, 2, "Pasta mit Gemüsebolognese"),
    (
        Canteen.STUCAFE_WEIHENSTEPHAN_MAXIMUS,
        454,
        2,
        "Burger mit Schinken und Käse überbacken, mit hausgemachter Burgersauce",
    ),
    (Canteen.MENSA_OTTOBRUNN, 433, 11, "Schweizer Knöpflepfanne mit feinem Gemüse und Käse"),
]


def response(content, url="https://example.org/"):
    return Mock(content=content, url=url, raise_for_status=Mock())


@pytest.mark.parametrize("canteen,url_id,dish_count,first_dish", CANTEENS)
def test_current_studentenwerk_sources(canteen, url_id, dish_count, first_dish):
    parser = get_menu_parsing_strategy(canteen)
    assert isinstance(parser, StudentenwerkMenuParser)
    assert canteen.url_id == url_id
    content = (ASSETS / f"{canteen.canteen_id}.html").read_bytes()
    with patch("menu_parser.requests.get", return_value=response(content)) as get:
        menus = parser.parse(canteen)
    get.assert_called_once_with(
        f"https://www.studierendenwerk-muenchen-oberbayern.de/gastronomie/speiseplan/speiseplan_{url_id}_-de.html",
        timeout=10.0,
    )
    assert list(menus) == [datetime.date(2026, 11, 4)]
    dishes = menus[datetime.date(2026, 11, 4)].dishes
    assert len(dishes) == dish_count
    assert dishes[0].name == first_dish
    assert Label.GLUTEN in dishes[0].labels


def test_dishes_keep_their_own_labels_with_missing_attributes_and_nested_titles():
    tree = html.fromstring(
        """<div class="c-schedule__item extra">
        <div class="extra c-schedule__header"><strong>04.11.2026</strong></div><ul>
        <li class="extra c-menu-dish-list__item" data-essen-fleischlos="2">
          <span class="stwm-artname extra">Pasta</span>
          <p class="extra c-menu-dish__title"> Pasta <b>mit Tomaten</b> </p></li>
        <li class="c-menu-dish-list__item" data-essen-allergene="Mi" data-essen-fleischlos="1">
          <span class="stwm-artname"> </span><p class="c-menu-dish__title">Käsenudeln</p></li>
        <li class="c-menu-dish-list__item" data-essen-allergene="Fi" data-essen-fleischlos="0">
          <span class="stwm-artname">Fisch</span><p class="c-menu-dish__title">Fisch</p></li>
        </ul></div>""",
    )
    menu = StudentenwerkMenuParser().get_menu(tree, Canteen.MENSA_PASING)
    assert [dish.name for dish in menu.dishes] == ["Pasta mit Tomaten", "Käsenudeln", "Fisch"]
    assert [dish.dish_type for dish in menu.dishes] == ["Pasta", "Pasta", "Fisch"]
    assert Label.VEGAN in menu.dishes[0].labels
    assert Label.MILK not in menu.dishes[0].labels
    assert Label.MILK in menu.dishes[1].labels
    assert Label.FISH in menu.dishes[2].labels
    assert Label.MEAT not in menu.dishes[2].labels


def test_parsing_keeps_days_after_invalid_date_without_mixing_days():
    first = (ASSETS / "stucafe-akademie-weihenstephan.html").read_text()
    last = first.replace("04.11.2026", "05.11.2026").replace("Pasta mit Gemüsebolognese", "Andere Pasta")
    broken = '<div class="extra c-schedule__item"><div class="c-schedule__header"><strong>closed</strong></div></div>'
    content = f"<html><body>{first}{broken}{last}</body></html>".encode()
    with (
        patch("menu_parser.requests.get", return_value=response(content)),
        pytest.warns(UserWarning, match="Problematic date: closed"),
    ):
        menus = StudentenwerkMenuParser().parse(Canteen.STUCAFE_AKADEMIE_WEIHENSTEPHAN)
    assert list(menus) == [datetime.date(2026, 11, 4), datetime.date(2026, 11, 5)]
    assert menus[datetime.date(2026, 11, 4)].dishes[0].name == "Pasta mit Gemüsebolognese"
    assert menus[datetime.date(2026, 11, 5)].dishes[0].name == "Andere Pasta"


def test_missing_date_is_skipped():
    with pytest.warns(UserWarning, match="Missing date"):
        assert StudentenwerkMenuParser().get_menu(html.fromstring("<div/>"), Canteen.MENSA_PASING) is None


def test_studentenwerk_timeout_is_reported():
    with (
        patch("menu_parser.requests.get", side_effect=requests.Timeout("timed out")),
        pytest.warns(UserWarning, match="Could not fetch menu for mensa-martinsried"),
    ):
        assert not StudentenwerkMenuParser().parse(Canteen.MENSA_MARTINSRIED)


def test_empty_studentenwerk_page_is_reported():
    with (
        patch("menu_parser.requests.get", return_value=response(b"<html><body>No menu</body></html>")),
        pytest.warns(UserWarning, match="No daily menus found"),
    ):
        assert not StudentenwerkMenuParser().parse(Canteen.MENSA_PASING)


def test_published_fmi_pdf_links_preserve_paths_and_queries():
    tree = html.fromstring(
        """<div>
        <a href="/.cm4all/uproc.php/0/Speiseplan_Garching_KW01_2027.pdf?_=123&amp;cdp=a">Next week</a>
        <a href="https://www.wilhelm-gastronomie.de/menus/Speiseplan_Garching_KW53_2026.pdf">This week</a>
        <a href="/Speiseplan_Grosshadern_KW53_2026.pdf">Other restaurant</a>
        <a href="/Speiseplan_Garching_KW54_2026.pdf">Invalid week</a>
        </div>""",
    )
    assert FMIBistroMenuParser.get_pdf_links(tree, FMIBistroMenuParser.menu_page_url) == {
        (
            2027,
            1,
        ): "https://www.wilhelm-gastronomie.de/.cm4all/uproc.php/0/Speiseplan_Garching_KW01_2027.pdf?_=123&cdp=a",
        (2026, 53): "https://www.wilhelm-gastronomie.de/menus/Speiseplan_Garching_KW53_2026.pdf",
    }


def test_fmi_uses_published_links_across_iso_year_boundary():
    parser = FMIBistroMenuParser()
    page = response(
        b'<a href="/new/Speiseplan_Garching_KW53_2026.pdf?download=1">Menu</a>'
        b'<a href="/new/Speiseplan_Garching_KW01_2027.pdf">Menu</a>',
        parser.menu_page_url,
    )
    parsed = [{datetime.date(2026, 12, 28): Mock()}, {datetime.date(2027, 1, 4): Mock()}]

    def convert_pdf(args):
        # Check that the temporary PDF was flushed before invoking the converter.
        assert Path(args[2]).read_bytes() == b"%PDF-test"
        Path(args[3]).write_text("menu text", encoding="utf-8")
        return 0

    today = datetime.date(2026, 12, 28)
    with patch("menu_parser.datetime.date") as date_class:
        date_class.today.return_value = today
        with (
            patch(
                "menu_parser.requests.get", side_effect=[page, response(b"%PDF-test"), response(b"%PDF-test")]
            ) as get,
            patch("menu_parser.call", side_effect=convert_pdf),
            patch.object(parser, "get_menus", side_effect=parsed) as parse,
        ):
            menus = parser.parse(Canteen.FMI_BISTRO)
    assert len(menus) == 2
    assert [call.args[0] for call in get.call_args_list] == [
        parser.menu_page_url,
        "https://www.wilhelm-gastronomie.de/new/Speiseplan_Garching_KW53_2026.pdf?download=1",
        "https://www.wilhelm-gastronomie.de/new/Speiseplan_Garching_KW01_2027.pdf",
    ]
    assert [call.args[1:] for call in parse.call_args_list] == [(2026, 53), (2027, 1)]


def test_missing_fmi_source_is_reported_without_inventing_menus():
    parser = FMIBistroMenuParser()
    with (
        patch(
            "menu_parser.requests.get",
            side_effect=[response(b"<html/>"), requests.HTTPError("404"), requests.Timeout()],
        ),
        pytest.warns(UserWarning, match="FMI menu unavailable") as warnings,
    ):
        assert not parser.parse(Canteen.FMI_BISTRO)
    assert len(warnings) == 2


@pytest.mark.parametrize("conversion_result", [1, 0])
def test_fmi_invalid_pdf_or_conversion_is_reported(conversion_result):
    parser = FMIBistroMenuParser()
    with (
        patch(
            "menu_parser.requests.get", side_effect=[response(b"<html/>"), response(b"%PDF-test"), response(b"HTML")]
        ),
        patch("menu_parser.call", return_value=conversion_result),
        patch.object(parser, "get_menus", side_effect=ParsingError("Unexpected layout")),
        pytest.warns(UserWarning, match="FMI menu unavailable") as warnings,
    ):
        assert not parser.parse(Canteen.FMI_BISTRO)
    assert len(warnings) == 2
