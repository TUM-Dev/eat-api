#!/bin/bash

set -e

CANTEEN_LIST=$(uv run src/main.py --canteen-ids)
OUT_DIR="${OUT_DIR:-dist}"

# Delete old output directory if it exists:
if [ -d $OUT_DIR ]; then
		rm -r $OUT_DIR
fi
# Create empty output directory:
mkdir -p $OUT_DIR
# keep translations cache
mv cache/en "$OUT_DIR/en"

parse(){
    echo "Parsing menus for $1..."
    uv run src/main.py -p "$1" -j "./$OUT_DIR/$1" -c
    echo "Parsing menus for $1 done."
}

# single failing canteen should not impact others
set +e
# Parse all canteens:
for canteen in ${CANTEEN_LIST};
do
 ( parse $canteen $LANGUAGE ) &
done
wait # Wait for all processes to finish
set -e

# Combine all combined.json files to one all.json file:
uv run scripts/combine.py

# do not translate outdated all_refs.json
uv run src/translate.py "$OUT_DIR" "$OUT_DIR/en" EN-US
# Remove all dishes which are older than one day
# and reorganize them in a more efficient format:
uv run scripts/reformat.py

openmensa_list=("fmi-bistro" )

# single failing canteen should not impact others
set +e
for CANTEEN in "${openmensa_list[@]}"; do
    echo "Parsing openmensa menus for: " "$CANTEEN"
    uv run src/main.py -p "$CANTEEN" --openmensa "$OUT_DIR/$CANTEEN"
done
set -e

ENUM_JSON_PATH="$OUT_DIR/enums"
mkdir -p "$ENUM_JSON_PATH"
echo "Creating Canteen-, Language- and Label-Enum"
uv run ./src/enum_json_creator.py "$ENUM_JSON_PATH"

# Copy canteens.json in the output directory (for backwards compatibility):
echo "Copying canteens..."
cp "$ENUM_JSON_PATH/canteens.json" $OUT_DIR
echo "Done"

tree "$OUT_DIR"
