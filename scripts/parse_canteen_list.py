# script to show canteen_ids from json output line by line

import json
import sys

if __name__ == "__main__":
    canteens = json.load(sys.stdin)
    for canteen in canteens:
        print(canteen["canteen_id"])
