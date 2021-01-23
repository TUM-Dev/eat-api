# -*- coding: utf-8 -*-

from datetime import datetime

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
