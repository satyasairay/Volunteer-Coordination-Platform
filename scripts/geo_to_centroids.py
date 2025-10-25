#!/usr/bin/env python3
"""
Convert Bhadrak 2011 census GeoJSON to villages CSV with centroids and bounding boxes.
Usage: python scripts/geo_to_centroids.py bhadrak_2011.geojson villages.csv
"""

import sys
import csv
import geojson
from shapely.geometry import shape
from shapely import simplify


def process_geojson(input_file, output_file):
    print(f"Reading {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = geojson.load(f)
    
    villages = []
    
    for feature in data['features']:
        try:
            props = feature['properties']
            geom = shape(feature['geometry'])
            
            simplified = simplify(geom, tolerance=0.001)
            
            centroid = simplified.centroid
            bounds = simplified.bounds
            
            village = {
                'name': props.get('name', props.get('NAME', 'Unknown')),
                'block': props.get('block', props.get('BLOCK', props.get('subdist', 'Unknown'))),
                'lat': round(centroid.y, 6),
                'lng': round(centroid.x, 6),
                'south': round(bounds[1], 6),
                'west': round(bounds[0], 6),
                'north': round(bounds[3], 6),
                'east': round(bounds[2], 6),
                'code_2011': props.get('censuscode', props.get('code', ''))
            }
            
            villages.append(village)
            
        except Exception as e:
            print(f"Error processing feature: {e}")
            continue
    
    print(f"Writing {len(villages)} villages to {output_file}...")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['name', 'block', 'lat', 'lng', 'south', 'west', 'north', 'east', 'code_2011']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(villages)
    
    print(f"✓ Done! Converted {len(villages)} villages.")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python geo_to_centroids.py <input.geojson> <output.csv>")
        sys.exit(1)
    
    process_geojson(sys.argv[1], sys.argv[2])
