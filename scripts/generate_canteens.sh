#!/bin/bash

# Generates the placeholder contents for the canteens.json file

loc_list=( "mensa-arcisstr" "mensa-arcisstrasse" "mensa-garching" "mensa-leopoldstr" "mensa-lothstr" \
"mensa-martinsried" "mensa-pasing" "mensa-weihenstephan" "stubistro-arcisstr" "stubistro-goethestr" \
"stubistro-großhadern" "stubistro-grosshadern" "stubistro-rosenheim" "stubistro-schellingstr" "stucafe-adalbertstr" \
"stucafe-akademie-weihenstephan" "stucafe-boltzmannstr" "stucafe-garching" "stucafe-karlstr" "stucafe-pasing" \
"ipp-bistro" "fmi-bistro" )

echo '{"canteens": ['
for loc in "${loc_list[@]}"; do
	echo '{ "location": {'
	echo '"lan": 2222,'
	echo '"long": 3333},'
	echo '"name": "NAME",'
    echo '"canteen_id": "'"$loc"'"},'
done
echo "]}"
