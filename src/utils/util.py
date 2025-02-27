# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from datetime import date, datetime
from typing import TYPE_CHECKING, Dict

import deepl

if TYPE_CHECKING:
    from src.entities import Menu

date_pattern = "%d.%m.%Y"
cli_date_format = "dd.mm.yyyy"


def parse_date(date_str):
    return datetime.strptime(date_str, date_pattern).date()


def make_duplicates_unique(names_with_duplicates):
    counts = [1] * len(names_with_duplicates)
    checked_names = []
    for i, name in enumerate(names_with_duplicates):
        if name in checked_names:
            counts[i] += 1
        checked_names.append(name)

    names_without_duplicates = names_with_duplicates
    for i, count in enumerate(counts):
        if count > 1:
            names_without_duplicates[i] += f" ({count})"

    return names_without_duplicates


def translate_dishes(menus: Dict[date, Menu], language: str) -> None:
    """
    Translate the dish titles of a menu. Source language is always german.

    :param menus: Menus dictionary as given by the menu parser, will be modified
    :param language: Identifier for a language
    :return: Whether translation was successful
    """
    # get api key from environment, abort if not given
    deepl_api_key = os.environ.get("DEEPL_API_KEY_EAT_API")
    if deepl_api_key is None:
        raise ValueError("For translation please provide a DeepL api key via DEEPL_API_KEY_EAT_API")

    translator = deepl.Translator(deepl_api_key)

    # batch dish names to prevent being rate limited
    for menu in menus.values():
        batch = [dish.name for dish in menu.dishes]
        results = translator.translate_text(batch, source_lang="DE", target_lang=language)
        for dish, name in zip(menu.dishes, results):
            dish.name = name
