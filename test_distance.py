#!/usr/bin/env python3
"""
Test script to verify distance calculation for Ahmedabad locations
"""

from services.route_service import RouteService


def test_ahmedabad_distance():
    """Test distance calculation for Ahmedabad locations"""
    route_service = RouteService()

    # Test the specific locations from the image
    origin = "pushpakunj, kankaria"
    destination = "shivalik v, paldi"

    print(f"Testing distance calculation:")
    print(f"Origin: {origin}")
    print(f"Destination: {destination}")
    print("-" * 50)

    # Test geocoding
    print("Testing geocoding...")
    origin_coords = route_service._geocode_location(origin)
    dest_coords = route_service._geocode_location(destination)

    print(f"Origin coordinates: {origin_coords}")
    print(f"Destination coordinates: {dest_coords}")

    # Test distance calculation
    print("\nTesting distance calculation...")
    distance = route_service._estimate_distance(origin, destination)
    print(f"Calculated distance: {distance} km")

    # Test route suggestions
    print("\nTesting route suggestions...")
    routes = route_service.suggest_routes(origin, destination, "bike")

    print(f"Real distance: {routes['real_distance_km']} km")
    print(f"Route 1 distance: {routes['routes'][0]['distance_km']} km")
    print(f"Route 2 distance: {routes['routes'][1]['distance_km']} km")

    return distance


if __name__ == "__main__":
    test_ahmedabad_distance()
