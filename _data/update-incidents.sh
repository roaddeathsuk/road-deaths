#!/bin/sh

python3 _data/generate-pages.py

git add _data/incidents.yml _data/annual_stats.yml _data/vehicle_types.yml index.html

git commit -m "Updated incidents"

git push --all -v
