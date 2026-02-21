"""
AI Service for real-time weather and traffic analysis using Gemini API
"""

import os
import datetime
from google import genai
from google.genai import types
from config import GEMINI_API_KEY


class AIService:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Gemini client"""
        if self.api_key and self.api_key != "demo_key":
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Error initializing Gemini client: {e}")
                self.client = None
        else:
            self.client = None

    def create_grounding_config(self):
        """Create grounding configuration with Google Search tool"""
        if self.client is None:
            return None

        try:
            grounding_tool = types.Tool(google_search=types.GoogleSearch())
            config = types.GenerateContentConfig(tools=[grounding_tool])
            return config
        except Exception as e:
            print(f"Error creating grounding config: {e}")
            return None

    def get_realtime_conditions(self, origin, destination):
        """
        Get real-time weather and traffic conditions for the route

        Args:
            origin (str): Starting location
            destination (str): Destination location

        Returns:
            dict: Weather and traffic analysis with multipliers
        """
        if self.client is None:
            return self._get_demo_conditions(origin, destination)

        try:
            current_time_ist = datetime.datetime.now(
                datetime.timezone(datetime.timedelta(hours=5, minutes=30))
            )

            prompt = f"""Please search for current weather and traffic conditions for a ride from {origin} to {destination} in India. 
            Current time is {current_time_ist.strftime('%Y-%m-%d %H:%M:%S IST')}.
            Focus on factors that would affect ride pricing such as:
            - Current weather conditions (rain, snow, clear skies, temperature)
            - Traffic congestion levels and road conditions
            - Any special events, road closures, or construction
            - Real-time traffic delays or incidents
            
            Please provide a brief summary of current conditions that would impact ride pricing."""

            config = self.create_grounding_config()
            if config is None:
                return self._get_demo_conditions(origin, destination)

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config,
            )

            return self._parse_conditions(response.text)

        except Exception as e:
            print(f"Error fetching real-time conditions: {e}")
            return self._get_demo_conditions(origin, destination)

    def _get_demo_conditions(self, origin, destination):
        """Return demo conditions when API is not available"""
        return {
            "weather": "clear",
            "traffic": "moderate",
            "weather_multiplier": 1.0,
            "traffic_multiplier": 1.4,
            "description": f"Demo conditions for {origin} to {destination}: Clear weather with moderate traffic",
            "is_demo": True,
        }

    def validate_place_in_city(self, place: str, city: str) -> bool:
        """
        Validate if a place exists in the given city using Gemini grounding search

        Args:
            place (str): Place name to validate
            city (str): City name

        Returns:
            bool: True if place exists in city
        """
        if self.client is None:
            return self._demo_place_validation(place, city)

        try:
            prompt = f"""Please search for information about "{place}" in "{city}", India.
            
            I need to know if this place actually exists in the specified city.
            Please provide:
            1. Confirmation if the place exists in {city}
            2. Brief description of the place if it exists
            3. Any alternative names or nearby locations if the exact place is not found
            
            Focus on verifying the location accuracy and providing helpful information."""

            config = self.create_grounding_config()
            if config is None:
                return self._demo_place_validation(place, city)

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config,
            )

            return self._parse_place_validation(response.text, place, city)

        except Exception as e:
            print(f"Error validating place with Gemini: {e}")
            return self._demo_place_validation(place, city)

    def get_city_suggestions(self, city: str) -> list:
        """
        Get famous places suggestions for a city using Gemini grounding search

        Args:
            city (str): City name

        Returns:
            list: List of famous places in the city
        """
        if self.client is None:
            return self._demo_city_suggestions(city)

        try:
            prompt = f"""Please search for famous places, landmarks, and popular locations in "{city}", India.
            
            I need a list of well-known places that tourists and locals would recognize.
            Please provide:
            1. Historical monuments and landmarks
            2. Popular tourist attractions
            3. Famous markets and commercial areas
            4. Important religious sites
            5. Parks and recreational areas
            6. Transportation hubs (airports, railway stations, bus stands)
            
            Format as a simple list of place names, one per line."""

            config = self.create_grounding_config()
            if config is None:
                return self._demo_city_suggestions(city)

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config,
            )

            return self._parse_city_suggestions(response.text)

        except Exception as e:
            print(f"Error getting city suggestions with Gemini: {e}")
            return self._demo_city_suggestions(city)

    def _demo_place_validation(self, place: str, city: str) -> bool:
        """Demo place validation when API is not available"""
        # Simple demo validation - accept if place contains city name or common terms
        place_lower = place.lower()
        city_lower = city.lower()

        # Accept if place contains city name
        if city_lower in place_lower:
            return True

        # Accept common place types
        common_terms = [
            "station",
            "airport",
            "hospital",
            "school",
            "college",
            "university",
            "market",
            "mall",
            "park",
            "temple",
            "church",
            "mosque",
            "gurudwara",
            "hotel",
            "restaurant",
            "office",
            "building",
            "road",
            "street",
            "area",
        ]

        return any(term in place_lower for term in common_terms)

    def _demo_city_suggestions(self, city: str) -> list:
        """Demo city suggestions when API is not available"""
        # Return some generic suggestions based on city
        suggestions = {
            "mumbai": [
                "Gateway of India",
                "Marine Drive",
                "Juhu Beach",
                "Bandra-Worli Sea Link",
            ],
            "delhi": ["Red Fort", "India Gate", "Qutub Minar", "Lotus Temple"],
            "bangalore": [
                "Cubbon Park",
                "Lalbagh",
                "Vidhana Soudha",
                "Bangalore Palace",
            ],
            "chennai": ["Marina Beach", "Kapaleeshwarar Temple", "Fort St. George"],
            "pune": ["Shaniwar Wada", "Aga Khan Palace", "Sinhagad Fort"],
        }

        return suggestions.get(
            city.lower(), ["City Center", "Main Market", "Railway Station", "Bus Stand"]
        )

    def _parse_place_validation(
        self, response_text: str, place: str, city: str
    ) -> bool:
        """Parse Gemini response to determine if place exists in city"""
        response_lower = response_text.lower()

        # Look for positive indicators
        positive_indicators = [
            "yes",
            "exists",
            "located",
            "found",
            "is in",
            "can be found",
            "situated",
            "present",
            "available",
            "real",
            "actual",
        ]

        # Look for negative indicators
        negative_indicators = [
            "no",
            "not found",
            "does not exist",
            "not located",
            "not in",
            "not available",
            "not present",
            "not real",
            "not actual",
            "incorrect",
        ]

        # Check for positive indicators
        for indicator in positive_indicators:
            if indicator in response_lower:
                return True

        # Check for negative indicators
        for indicator in negative_indicators:
            if indicator in response_lower:
                return False

        # If unclear, check if place name appears in response
        if place.lower() in response_lower and city.lower() in response_lower:
            return True

        # Default to false if unclear
        return False

    def _parse_city_suggestions(self, response_text: str) -> list:
        """Parse Gemini response to extract city suggestions"""
        lines = response_text.split("\n")
        suggestions = []

        for line in lines:
            line = line.strip()
            # Skip empty lines and common prefixes
            if not line or line.startswith(
                ("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "-", "*", "•")
            ):
                continue

            # Clean up the line
            line = line.lstrip("123456789.-*• ").strip()
            if line and len(line) > 2:  # Only add meaningful suggestions
                suggestions.append(line)

        return suggestions[:15]  # Limit to 15 suggestions

    def _parse_conditions(self, response_text):
        """Parse AI response to extract weather and traffic conditions"""
        response_lower = response_text.lower()

        # Determine weather conditions
        weather = "clear"
        weather_multiplier = 1.0

        if "heavy rain" in response_lower or "heavy snowfall" in response_lower:
            weather = "heavy_rain"
            weather_multiplier = 1.5
        elif "light rain" in response_lower or "light drizzle" in response_lower:
            weather = "light_rain"
            weather_multiplier = 1.2
        elif "fog" in response_lower:
            weather = "fog"
            weather_multiplier = 1.3
        elif "storm" in response_lower:
            weather = "storm"
            weather_multiplier = 1.8

        # Determine traffic conditions
        traffic = "moderate"
        traffic_multiplier = 1.4

        if "heavy traffic" in response_lower or "traffic congestion" in response_lower:
            traffic = "heavy"
            traffic_multiplier = 1.8
        elif "severe traffic" in response_lower or "traffic jam" in response_lower:
            traffic = "severe"
            traffic_multiplier = 2.2
        elif "light traffic" in response_lower or "no traffic" in response_lower:
            traffic = "light"
            traffic_multiplier = 1.0

        return {
            "weather": weather,
            "traffic": traffic,
            "weather_multiplier": weather_multiplier,
            "traffic_multiplier": traffic_multiplier,
            "description": response_text,
            "is_demo": False,
        }
