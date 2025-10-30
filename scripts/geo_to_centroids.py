#!/usr/bin/env python3
"""
Convert Bhadrak 2011 census GeoJSON to villages CSV with centroids and bounding boxes.
Usage: python scripts/geo_to_centroids.py bhadrak_2011.geojson villages.csv
"""

import sys
import csv
from typing import Iterable, List, Tuple

import geojson


def iter_all_coords(geometry: dict) -> Iterable[Tuple[float, float]]:
    """Yield all coordinate pairs from a GeoJSON Polygon or MultiPolygon."""
    geom_type = geometry.get("type")
    coords = geometry.get("coordinates", [])

    if geom_type == "Polygon":
        for ring in coords:
            for x, y in ring:
                yield float(x), float(y)
    elif geom_type == "MultiPolygon":
        for polygon in coords:
            for ring in polygon:
                for x, y in ring:
                    yield float(x), float(y)
    else:
        raise ValueError(f"Unsupported geometry type: {geom_type}")


def polygon_area_centroid(ring: List[Tuple[float, float]]) -> Tuple[float, float, float]:
    """Return (area, cx, cy) for a single polygon ring."""
    if not ring:
        return 0.0, 0.0, 0.0

    # Ensure ring is closed
    if ring[0] != ring[-1]:
        ring = ring + [ring[0]]

    area = 0.0
    cx = 0.0
    cy = 0.0

    for (x0, y0), (x1, y1) in zip(ring[:-1], ring[1:]):
        cross = x0 * y1 - x1 * y0
        area += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross

    area *= 0.5
    if abs(area) < 1e-12:
        xs = [x for x, _ in ring]
        ys = [y for _, y in ring]
        return 0.0, sum(xs) / len(xs), sum(ys) / len(ys)

    cx /= (6.0 * area)
    cy /= (6.0 * area)
    return area, cx, cy


def compute_centroid(geometry: dict) -> Tuple[float, float]:
    """Compute centroid for Polygon or MultiPolygon without shapely."""
    geom_type = geometry.get("type")
    coords = geometry.get("coordinates", [])

    if geom_type == "Polygon":
        outer_ring = coords[0] if coords else []
        _, cx, cy = polygon_area_centroid([tuple(pt) for pt in outer_ring])
        return cx, cy

    if geom_type == "MultiPolygon":
        total_area = 0.0
        centroid_x = 0.0
        centroid_y = 0.0

        for polygon in coords:
            outer_ring = polygon[0] if polygon else []
            area, cx, cy = polygon_area_centroid([tuple(pt) for pt in outer_ring])
            total_area += area
            centroid_x += cx * area
            centroid_y += cy * area

        if abs(total_area) < 1e-12:
            pts = list(iter_all_coords(geometry))
            if not pts:
                return 0.0, 0.0
            xs = [x for x, _ in pts]
            ys = [y for _, y in pts]
            return sum(xs) / len(xs), sum(ys) / len(ys)

        return centroid_x / total_area, centroid_y / total_area

    raise ValueError(f"Unsupported geometry type: {geom_type}")


def process_geojson(input_file: str, output_file: str) -> None:
    print(f"Reading {input_file}...")

    with open(input_file, "r", encoding="utf-8") as f:
        data = geojson.load(f)

    villages = []

    for feature in data["features"]:
        try:
            props = feature["properties"]
            geometry = feature["geometry"]

            centroid_x, centroid_y = compute_centroid(geometry)

            xs = []
            ys = []
            for x, y in iter_all_coords(geometry):
                xs.append(x)
                ys.append(y)

            if not xs or not ys:
                raise ValueError("Empty coordinate list")

            village = {
                "name": props.get("name", props.get("NAME", "Unknown")),
                "block": props.get("block", props.get("BLOCK", props.get("subdist", "Unknown"))),
                "lat": round(centroid_y, 6),
                "lng": round(centroid_x, 6),
                "south": round(min(ys), 6),
                "west": round(min(xs), 6),
                "north": round(max(ys), 6),
                "east": round(max(xs), 6),
                "code_2011": props.get("censuscode", props.get("code", "")),
            }

            villages.append(village)

        except Exception as exc:
            print(f"Error processing feature: {exc}")
            continue

    print(f"Writing {len(villages)} villages to {output_file}...")

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["name", "block", "lat", "lng", "south", "west", "north", "east", "code_2011"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(villages)

    print(f"Done! Converted {len(villages)} villages.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python geo_to_centroids.py <input.geojson> <output.csv>")
        sys.exit(1)

    process_geojson(sys.argv[1], sys.argv[2])
