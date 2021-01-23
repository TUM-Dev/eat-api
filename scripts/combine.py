#!/bin/python3
import os
from typing import List


def main():
    if os.path.isdir("dist"):
        os.chdir("dist")
        files: List[str] = []

        combined_df_name: str = "combined"
        out_file_name: str = "all.json"

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

        with open(out_file_name, "w") as out_file:
            out_file.write('{"canteens": [\n')
            for i, file in enumerate(files):
                with open(file) as in_file:
                    for line in in_file:
                        out_file.write(line)
                    if i < len(files) - 1:
                        out_file.write(",")
            out_file.write("]}")


if __name__ == "__main__":
    main()
