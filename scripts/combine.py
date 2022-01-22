#!/bin/python3
import os
from typing import List
import json


def get_combined_str() -> str:
    os.chdir("dist")
    files: List[str] = []

    combined_df_name: str = "combined"

    for directory in os.listdir("."):
        if os.path.isdir(directory):
            os.chdir(directory)
            if os.path.isdir(combined_df_name):
                os.chdir(combined_df_name)
                if os.path.exists(combined_df_name + ".json"):
                    files.append(os.path.join(os.getcwd(), combined_df_name + ".json"))
                    print("Found " + combined_df_name + ".json for: " + directory)
                os.chdir("..")
            os.chdir("..")

    out_str: str = '{"canteens": [\n'
    for i, file in enumerate(files):
        with open(file, encoding="utf-8") as in_file:
            for line in in_file:
                out_str += line
            if i < len(files) - 1:
                out_str += ","
    out_str += "]}"
    return out_str


def main():
    if os.path.isdir("dist"):
        out_str: str = get_combined_str()
        out_file_name: str = "all.json"
        with open(out_file_name, "w", encoding="utf-8") as out_file:
            json.dump(json.loads(out_str), out_file, separators=(',', ':'))


if __name__ == "__main__":
    main()
