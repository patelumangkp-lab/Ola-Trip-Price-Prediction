"""
Route Service for calculating distances and suggesting routes
"""

import random
from typing import Dict, List, Tuple
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from config import VEHICLE_TYPES


class RouteService:
    def __init__(self):
        self.vehicle_types = VEHICLE_TYPES
        # Initialize geocoder with a user agent
        self.geolocator = Nominatim(user_agent="ride_price_prediction_app")

    def suggest_routes(self, origin: str, destination: str, vehicle_type: str) -> Dict:
        """
        Suggest optimal routes - one with traffic and one without traffic
        Includes places along the route for better user experience

        Args:
            origin (str): Starting location
            destination (str): Destination location
            vehicle_type (str): Type of vehicle

        Returns:
            dict: Route suggestions with distances, estimated times, and places along route
        """
        # Simulate route calculation (in real app, integrate with Google Maps API)
        base_distance = self._estimate_distance(origin, destination)

        # Get places along the route
        places_along_route = self._get_places_along_route(origin, destination)

        # Route 1: Optimal route with traffic considerations (faster but more expensive)
        route1 = {
            "id": "route_1",
            "name": "Fastest Route (With Traffic)",
            "distance_km": round(base_distance * 1.1, 1),
            "estimated_time_minutes": round(
                base_distance * 1.1 * 2.2, 0
            ),  # 2.2 min per km with moderate traffic
            "traffic_level": "moderate",
            "description": "Uses highways and main roads, optimized for speed with traffic considerations",
            "route_points": self._generate_route_points(
                origin, destination, "highway_route"
            ),
            "places_along_route": places_along_route[:4],  # First 4 places
            "route_type": "highway",
            "fuel_efficiency": "moderate",
            "comfort_level": "high",
        }

        # Route 2: Scenic route with less traffic (longer but more comfortable)
        route2 = {
            "id": "route_2",
            "name": "Scenic Route (Less Traffic)",
            "distance_km": round(base_distance * 1.3, 1),
            "estimated_time_minutes": round(
                base_distance * 1.3 * 1.5, 0
            ),  # 1.5 min per km without traffic
            "traffic_level": "light",
            "description": "Uses scenic routes and local roads, less traffic but longer distance",
            "route_points": self._generate_route_points(
                origin, destination, "scenic_route"
            ),
            "places_along_route": places_along_route[4:8],  # Next 4 places
            "route_type": "scenic",
            "fuel_efficiency": "high",
            "comfort_level": "very_high",
        }

        # Get real coordinates for origin and destination
        origin_coords = self._geocode_location(origin)
        destination_coords = self._geocode_location(destination)

        return {
            "origin": origin,
            "destination": destination,
            "vehicle_type": vehicle_type,
            "routes": [route1, route2],
            "total_places_along_route": len(places_along_route),
            "origin_coordinates": origin_coords,
            "destination_coordinates": destination_coords,
            "real_distance_km": self._estimate_distance(origin, destination),
        }

    def _estimate_distance(self, origin: str, destination: str) -> float:
        """
        Calculate real distance between two locations using geopy
        """
        try:
            print(f"Calculating distance from '{origin}' to '{destination}'")

            # Geocode the origin location
            origin_location = self._geocode_location(origin)
            if not origin_location:
                print(f"Failed to geocode origin '{origin}', using fallback")
                return self._fallback_distance_calculation(origin, destination)

            # Geocode the destination location
            destination_location = self._geocode_location(destination)
            if not destination_location:
                print(f"Failed to geocode destination '{destination}', using fallback")
                return self._fallback_distance_calculation(origin, destination)

            print(f"Origin coordinates: {origin_location}")
            print(f"Destination coordinates: {destination_location}")

            # Calculate distance using geodesic calculation
            distance = geodesic(origin_location, destination_location).kilometers
            distance = round(distance, 1)
            print(f"Raw calculated distance: {distance} km")

            # Validate the distance is reasonable
            validated_distance = self._validate_distance(distance, origin, destination)
            print(f"Final validated distance: {validated_distance} km")
            return validated_distance

        except Exception as e:
            print(f"Error calculating distance: {e}")
            return self._fallback_distance_calculation(origin, destination)

    def _geocode_location(self, location: str) -> Tuple[float, float]:
        """
        Geocode a location string to get latitude and longitude
        """
        try:
            # Add India to the location string for better geocoding
            location_with_country = f"{location}, India"
            geocoded = self.geolocator.geocode(location_with_country, timeout=10)

            if geocoded:
                return (geocoded.latitude, geocoded.longitude)
            else:
                # Try without country suffix
                geocoded = self.geolocator.geocode(location, timeout=10)
                if geocoded:
                    return (geocoded.latitude, geocoded.longitude)

                # Try with Ahmedabad-specific formatting for better results
                if "ahmedabad" in location.lower():
                    # Try with Gujarat state for Ahmedabad locations
                    location_with_state = f"{location}, Gujarat, India"
                    geocoded = self.geolocator.geocode(location_with_state, timeout=10)
                    if geocoded:
                        return (geocoded.latitude, geocoded.longitude)

                    # Try with known Ahmedabad area coordinates
                    ahmedabad_coords = self._get_ahmedabad_coordinates(location)
                    if ahmedabad_coords:
                        return ahmedabad_coords

                return None

        except Exception as e:
            print(f"Error geocoding location '{location}': {e}")
            return None

    def _fallback_distance_calculation(self, origin: str, destination: str) -> float:
        """
        Fallback distance calculation using predefined city distances and smart estimation
        """
        print(f"Using fallback distance calculation for '{origin}' to '{destination}'")
        # Known city distances for fallback
        city_distances = {
            ("Mumbai", "Delhi"): 1400,
            ("Mumbai", "Bangalore"): 850,
            ("Delhi", "Bangalore"): 2200,
            ("Mumbai", "Pune"): 150,
            ("Delhi", "Gurgaon"): 30,
            ("Bangalore", "Chennai"): 350,
            ("Mumbai", "Ahmedabad"): 530,
            ("Delhi", "Jaipur"): 280,
            ("Bangalore", "Hyderabad"): 570,
            ("Mumbai", "Nashik"): 180,
            ("Delhi", "Noida"): 25,
            ("Mumbai", "Thane"): 35,
            ("Bangalore", "Mysore"): 150,
            ("Chennai", "Coimbatore"): 500,
            ("Kolkata", "Howrah"): 5,
        }

        # Known Ahmedabad area distances for more accurate local estimation
        ahmedabad_areas = {
            ("kankaria", "paldi"): 8,
            ("pushpakunj", "paldi"): 8,  # pushpakunj is near kankaria
            ("kankaria", "shivalik"): 8,  # shivalik is in paldi
            ("pushpakunj", "shivalik"): 8,  # pushpakunj to shivalik
            ("kankaria", "maninagar"): 3,
            ("paldi", "maninagar"): 6,
            ("kankaria", "vadaj"): 12,
            ("paldi", "vadaj"): 8,
            ("kankaria", "bapunagar"): 5,
            ("paldi", "bapunagar"): 7,
            ("kankaria", "navrangpura"): 4,
            ("paldi", "navrangpura"): 2,
            ("kankaria", "cg road"): 6,
            ("paldi", "cg road"): 3,
            ("kankaria", "sabarmati"): 15,
            ("paldi", "sabarmati"): 12,
        }

        # Check for Ahmedabad area pairs
        origin_lower = origin.lower()
        destination_lower = destination.lower()

        print(f"Checking Ahmedabad areas for '{origin_lower}' to '{destination_lower}'")

        for (area1, area2), distance in ahmedabad_areas.items():
            if (area1 in origin_lower and area2 in destination_lower) or (
                area2 in origin_lower and area1 in destination_lower
            ):
                print(f"Found Ahmedabad area match: {area1}-{area2} = {distance} km")
                return distance

        # Check for exact city pairs
        for (city1, city2), distance in city_distances.items():
            if (
                city1.lower() in origin.lower() and city2.lower() in destination.lower()
            ) or (
                city2.lower() in origin.lower() and city1.lower() in destination.lower()
            ):
                return distance

        # Check if both locations are in the same city
        origin_city = self._extract_city_name(origin)
        destination_city = self._extract_city_name(destination)

        if origin_city.lower() == destination_city.lower():
            # Same city - use realistic intra-city distance
            return random.uniform(2, 15)  # 2-15 km for same city locations

        # Different cities - use a more reasonable estimation
        # Try to extract city names and estimate based on known distances
        origin_lower = origin.lower()
        destination_lower = destination.lower()

        # Check for major city patterns
        major_cities = {
            "mumbai": "Mumbai",
            "delhi": "Delhi",
            "bangalore": "Bangalore",
            "chennai": "Chennai",
            "kolkata": "Kolkata",
            "hyderabad": "Hyderabad",
            "pune": "Pune",
            "ahmedabad": "Ahmedabad",
            "jaipur": "Jaipur",
        }

        origin_city_found = None
        dest_city_found = None

        for city_key, city_name in major_cities.items():
            if city_key in origin_lower:
                origin_city_found = city_name
            if city_key in destination_lower:
                dest_city_found = city_name

        # If we found both cities, try to get distance from our known distances
        if origin_city_found and dest_city_found:
            for (city1, city2), distance in city_distances.items():
                if (city1 == origin_city_found and city2 == dest_city_found) or (
                    city2 == origin_city_found and city1 == dest_city_found
                ):
                    return distance

        # If one location is in a major city, estimate based on city size
        if origin_city_found or dest_city_found:
            # Major city to unknown location - estimate 20-100 km
            return random.uniform(20, 100)

        # Both locations unknown - use conservative estimation
        return random.uniform(5, 25)  # 5-25 km for unknown locations

    def _validate_distance(
        self, distance: float, origin: str, destination: str
    ) -> float:
        """
        Validate that the calculated distance is reasonable for the given locations
        """
        origin_city = self._extract_city_name(origin)
        destination_city = self._extract_city_name(destination)

        # If both locations are in the same city, distance should be reasonable for intra-city travel
        if origin_city.lower() == destination_city.lower():
            # For same city, maximum reasonable distance is 50 km
            if distance > 50:
                print(
                    f"Distance {distance} km seems too large for same city travel. Using fallback."
                )
                return self._fallback_distance_calculation(origin, destination)
            # For same city, minimum reasonable distance is 0.5 km
            elif distance < 0.5:
                print(f"Distance {distance} km seems too small. Using fallback.")
                return self._fallback_distance_calculation(origin, destination)

        # For different cities, check if distance is reasonable
        else:
            # If distance is less than 5 km for different cities, it might be wrong
            if distance < 5:
                print(
                    f"Distance {distance} km seems too small for inter-city travel. Using fallback."
                )
                return self._fallback_distance_calculation(origin, destination)

        return distance

    def _get_ahmedabad_coordinates(self, location: str) -> Tuple[float, float]:
        """
        Get coordinates for known Ahmedabad areas
        """
        location_lower = location.lower()

        # Known Ahmedabad area coordinates
        ahmedabad_coordinates = {
            "kankaria": (23.0081, 72.6027),
            "paldi": (23.0225, 72.5714),
            "maninagar": (23.0125, 72.6125),
            "vadaj": (23.0800, 72.5800),
            "bapunagar": (23.0400, 72.6200),
            "navrangpura": (23.0300, 72.5600),
            "cg road": (23.0300, 72.5600),
            "sabarmati": (23.0800, 72.5800),
            "pushpakunj": (23.0081, 72.6027),  # Near Kankaria
            "shivalik": (23.0225, 72.5714),  # Near Paldi
            "shivalik v": (23.0225, 72.5714),  # Shivalik V in Paldi
        }

        # Check for area matches
        for area, coords in ahmedabad_coordinates.items():
            if area in location_lower:
                return coords

        # Default to Ahmedabad city center if no specific area found
        return (23.0225, 72.5714)  # Ahmedabad city center

    def _get_places_along_route(self, origin: str, destination: str) -> List[Dict]:
        """
        Get places along the route between origin and destination
        Uses real geocoding data for more accurate place suggestions
        """
        places = []

        # Extract city names for better place suggestions
        origin_city = self._extract_city_name(origin)
        destination_city = self._extract_city_name(destination)

        # Get coordinates for distance calculations
        origin_coords = self._geocode_location(origin)
        destination_coords = self._geocode_location(destination)

        # Common places that might be along routes
        common_places = [
            {
                "name": "City Center",
                "type": "commercial",
                "description": "Main commercial area",
            },
            {
                "name": "Railway Station",
                "type": "transport",
                "description": "Major railway station",
            },
            {
                "name": "Shopping Mall",
                "type": "commercial",
                "description": "Popular shopping destination",
            },
            {"name": "Hospital", "type": "essential", "description": "Major hospital"},
            {
                "name": "University",
                "type": "educational",
                "description": "Educational institution",
            },
            {
                "name": "Park",
                "type": "recreation",
                "description": "Public park or garden",
            },
            {"name": "Temple", "type": "religious", "description": "Religious site"},
            {
                "name": "Market",
                "type": "commercial",
                "description": "Local market area",
            },
            {"name": "Airport", "type": "transport", "description": "Airport terminal"},
            {
                "name": "Bus Stand",
                "type": "transport",
                "description": "Main bus terminal",
            },
        ]

        # Generate 8-10 places along the route
        import random

        selected_places = random.sample(common_places, min(8, len(common_places)))

        for i, place in enumerate(selected_places):
            # Calculate more realistic distance based on route position
            if origin_coords and destination_coords:
                # Calculate total distance
                total_distance = geodesic(origin_coords, destination_coords).kilometers
                # Distribute places along the route
                distance_ratio = (
                    i / (len(selected_places) - 1) if len(selected_places) > 1 else 0
                )
                distance_from_origin = round(total_distance * distance_ratio, 1)
            else:
                # Fallback to random distance
                distance_from_origin = round(random.uniform(5, 50), 1)

            places.append(
                {
                    "name": (
                        f"{place['name']} ({origin_city})"
                        if i < 4
                        else f"{place['name']} ({destination_city})"
                    ),
                    "type": place["type"],
                    "description": place["description"],
                    "distance_from_origin": distance_from_origin,
                    "estimated_stop_time": random.choice([5, 10, 15, 20]),
                    "coordinates": self._get_place_coordinates(
                        place["name"], origin_city if i < 4 else destination_city
                    ),
                }
            )

        return places

    def _get_place_coordinates(self, place_name: str, city: str) -> Tuple[float, float]:
        """
        Get coordinates for a specific place in a city
        """
        try:
            # Try to geocode the specific place
            place_query = f"{place_name}, {city}, India"
            geocoded = self.geolocator.geocode(place_query, timeout=5)

            if geocoded:
                return (geocoded.latitude, geocoded.longitude)
            else:
                # Fallback to city center coordinates
                city_coords = self._geocode_location(city)
                if city_coords:
                    # Add small random offset to simulate place location
                    import random

                    lat_offset = random.uniform(-0.01, 0.01)
                    lng_offset = random.uniform(-0.01, 0.01)
                    return (city_coords[0] + lat_offset, city_coords[1] + lng_offset)
                return None

        except Exception as e:
            print(f"Error getting coordinates for {place_name} in {city}: {e}")
            return None

    def _extract_city_name(self, location: str) -> str:
        """Extract city name from location string"""
        # Simple extraction - in real app, use geocoding
        if "," in location:
            return location.split(",")[-1].strip()
        return location

    def _generate_route_points(
        self, origin: str, destination: str, route_type: str
    ) -> List[Dict]:
        """
        Generate route waypoints for visualization using real coordinates
        """
        # Get real coordinates for origin and destination
        origin_coords = self._geocode_location(origin)
        destination_coords = self._geocode_location(destination)

        # Fallback coordinates (Mumbai) if geocoding fails
        if not origin_coords:
            origin_coords = (19.0760, 72.8777)
        if not destination_coords:
            destination_coords = (19.0760 + 0.04, 72.8777 + 0.04)

        if route_type == "highway_route":
            return self._generate_highway_route_points(
                origin, destination, origin_coords, destination_coords
            )
        elif route_type == "scenic_route":
            return self._generate_scenic_route_points(
                origin, destination, origin_coords, destination_coords
            )
        else:  # local_roads
            return self._generate_local_route_points(
                origin, destination, origin_coords, destination_coords
            )

    def _generate_highway_route_points(
        self,
        origin: str,
        destination: str,
        origin_coords: Tuple[float, float],
        destination_coords: Tuple[float, float],
    ) -> List[Dict]:
        """Generate highway route waypoints"""
        import random

        # Calculate intermediate points along the route
        lat_diff = destination_coords[0] - origin_coords[0]
        lng_diff = destination_coords[1] - origin_coords[1]

        return [
            {"lat": origin_coords[0], "lng": origin_coords[1], "name": origin},
            {
                "lat": origin_coords[0] + lat_diff * 0.25,
                "lng": origin_coords[1] + lng_diff * 0.25,
                "name": "Highway Junction",
            },
            {
                "lat": origin_coords[0] + lat_diff * 0.5,
                "lng": origin_coords[1] + lng_diff * 0.5,
                "name": "Toll Plaza",
            },
            {
                "lat": origin_coords[0] + lat_diff * 0.75,
                "lng": origin_coords[1] + lng_diff * 0.75,
                "name": "City Limits",
            },
            {
                "lat": destination_coords[0],
                "lng": destination_coords[1],
                "name": destination,
            },
        ]

    def _generate_scenic_route_points(
        self,
        origin: str,
        destination: str,
        origin_coords: Tuple[float, float],
        destination_coords: Tuple[float, float],
    ) -> List[Dict]:
        """Generate scenic route waypoints"""
        import random

        # Calculate intermediate points with slight variations for scenic route
        lat_diff = destination_coords[0] - origin_coords[0]
        lng_diff = destination_coords[1] - origin_coords[1]

        # Add some scenic variations
        scenic_variation = 0.01

        return [
            {"lat": origin_coords[0], "lng": origin_coords[1], "name": origin},
            {
                "lat": origin_coords[0]
                + lat_diff * 0.2
                + random.uniform(-scenic_variation, scenic_variation),
                "lng": origin_coords[1]
                + lng_diff * 0.2
                + random.uniform(-scenic_variation, scenic_variation),
                "name": "Local Road",
            },
            {
                "lat": origin_coords[0]
                + lat_diff * 0.4
                + random.uniform(-scenic_variation, scenic_variation),
                "lng": origin_coords[1]
                + lng_diff * 0.4
                + random.uniform(-scenic_variation, scenic_variation),
                "name": "Scenic Viewpoint",
            },
            {
                "lat": origin_coords[0]
                + lat_diff * 0.7
                + random.uniform(-scenic_variation, scenic_variation),
                "lng": origin_coords[1]
                + lng_diff * 0.7
                + random.uniform(-scenic_variation, scenic_variation),
                "name": "Park Area",
            },
            {
                "lat": destination_coords[0],
                "lng": destination_coords[1],
                "name": destination,
            },
        ]

    def _generate_local_route_points(
        self,
        origin: str,
        destination: str,
        origin_coords: Tuple[float, float],
        destination_coords: Tuple[float, float],
    ) -> List[Dict]:
        """Generate local route waypoints"""
        import random

        # Calculate intermediate points for local route
        lat_diff = destination_coords[0] - origin_coords[0]
        lng_diff = destination_coords[1] - origin_coords[1]

        return [
            {"lat": origin_coords[0], "lng": origin_coords[1], "name": origin},
            {
                "lat": origin_coords[0] + lat_diff * 0.33,
                "lng": origin_coords[1] + lng_diff * 0.33,
                "name": "Local Road",
            },
            {
                "lat": origin_coords[0] + lat_diff * 0.66,
                "lng": origin_coords[1] + lng_diff * 0.66,
                "name": "Shortcut",
            },
            {
                "lat": destination_coords[0],
                "lng": destination_coords[1],
                "name": destination,
            },
        ]

    def calculate_route_pricing(
        self, route: Dict, vehicle_type: str, conditions: Dict
    ) -> Dict:
        """
        Calculate pricing for a specific route

        Args:
            route (dict): Route information
            vehicle_type (str): Type of vehicle
            conditions (dict): Weather and traffic conditions

        Returns:
            dict: Pricing breakdown
        """
        vehicle_config = self.vehicle_types[vehicle_type]
        base_rate = vehicle_config["base_rate_per_km"]
        base_fare = vehicle_config["base_fare"]

        # Calculate base cost
        distance_km = route["distance_km"]
        base_cost = base_fare + (distance_km * base_rate)

        # Apply weather and traffic multipliers
        weather_multiplier = conditions.get("weather_multiplier", 1.0)
        traffic_multiplier = conditions.get("traffic_multiplier", 1.0)

        # Calculate final fare
        final_fare = base_cost * weather_multiplier * traffic_multiplier

        # Calculate driver earnings and company profit
        driver_earnings = final_fare * 0.75  # 75% to driver
        company_profit = final_fare * 0.25  # 25% to company

        return {
            "base_cost": round(base_cost, 2),
            "weather_multiplier": weather_multiplier,
            "traffic_multiplier": traffic_multiplier,
            "final_fare": round(final_fare, 2),
            "driver_earnings": round(driver_earnings, 2),
            "company_profit": round(company_profit, 2),
            "breakdown": {
                "base_fare": base_fare,
                "distance_cost": round(distance_km * base_rate, 2),
                "weather_adjustment": round(base_cost * (weather_multiplier - 1), 2),
                "traffic_adjustment": round(
                    base_cost * weather_multiplier * (traffic_multiplier - 1), 2
                ),
            },
        }
