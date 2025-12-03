# -*- coding: utf-8 -*-

import argparse
import json
import os
import pathlib
import sys

import deepl

from utils.file_util import load_json


class Translator:
    def __init__(self, api_key, cache_file, source="DE", target="EN-US"):
        self.api_key = api_key
        self.translator = deepl.Translator(api_key)
        self.source = source
        self.target = target
        self.cache_file = cache_file
        self.cache = {}

    def prefetch(self, texts):
        to_translate = {text for text in texts if text not in self.cache}
        if not to_translate:
            return

        result = self.translator.translate_text(to_translate, source_lang=self.source, target_lang=self.target)
        for original, translation in zip(to_translate, result):
            self.cache[original] = translation.text

    def translate(self, text):
        if text in self.cache:
            return self.cache[text]

        result = self.translator.translate_text(text, source_lang=self.source, target_lang=self.target)
        self.cache[text] = result.text
        return result.text

    def load_cache(self):
        self.cache = load_json(self.cache_file)

    def save_cache(self):
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, separators=(",", ":"), ensure_ascii=False, sort_keys=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Translates dishes, requires a DeepL API-Key in the environment variable DEEPL_API_KEY"
    )
    parser.add_argument(
        "input",
        help="input directory",
    )
    parser.add_argument(
        "output",
        help="directory for translated output",
    )
    parser.add_argument("language", help="The language to translate the dishes to")
    parser.add_argument("--source_language", default="DE", help="language the dishes are in")
    parser.add_argument("--no-cache", action="store_true", help="Do not write a cache file")

    args = parser.parse_args()
    input_dir = pathlib.Path(args.input)
    if not input_dir.is_dir():
        sys.exit(f"Input {input_dir} does not exist or is not a directory")

    output_dir = pathlib.Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    return args, input_dir, output_dir


def main():
    args, input_dir, output_dir = parse_args()

    deepl_api_key = os.getenv("DEEPL_API_KEY")
    cache_file = output_dir / "translations.json"
    translator = Translator(deepl_api_key, cache_file, args.source_language, args.language)
    if cache_file.is_file():
        translator.load_cache()
    elif not args.no_cache:
        print(f"No cache file {cache_file} found")

    try:
        for json_file in input_dir.rglob("*.json"):
            # prevent unlimited recursion
            if output_dir in json_file.parents:
                continue
            relative_path = json_file.relative_to(input_dir)
            output_path = output_dir / relative_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            translate_file(json_file, output_path, translator)
    # always update cache to prevent future rate-limits
    except deepl.exceptions.DeepLException as e:
        print(f"Error during translation: {e.with_traceback(sys.exc_info()[2])}")

    if not args.no_cache:
        translator.save_cache()


def translate_file(input_path, output_path, translator):
    print(f"Translating {input_path}")
    data = load_json(input_path)

    match input_path.name:
        case "all.json":
            for canteen in data["canteens"]:
                for week in canteen["weeks"]:
                    translate_days(week, translator)
        case "combined.json":
            for week in data["weeks"]:
                translate_days(week, translator)
        case _:
            translate_days(data, translator)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"), ensure_ascii=False)


def translate_days(data, translator):
    # batch translation to reduce API calls
    translator.prefetch({dish["name"] for day in data["days"] for dish in day["dishes"]})
    for day in data["days"]:
        for dish in day["dishes"]:
            dish["name"] = translator.translate(dish["name"])


if __name__ == "__main__":
    main()
