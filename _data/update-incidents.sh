#!/bin/sh

python3 _data/generate-pages.py

INCIDENT_FILES="_data/incidents.yml _data/annual_stats.yml _data/vehicle_types.yml index.html"

git add ${INCIDENT_FILES}

git commit -m "Updated incidents" ${INCIDENT_FILES}

git push --all -v
