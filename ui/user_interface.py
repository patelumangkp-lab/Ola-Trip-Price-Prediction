"""
Streamlit User Interface for Cab Service Booking
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import folium
from streamlit_folium import st_folium

from services.ai_service import AIService
from services.route_service import RouteService
from services.booking_service import BookingService
from services.auth_service import AuthService
from services.database_service import DatabaseService
from config import VEHICLE_TYPES, INDIAN_CITIES, APP_TITLE, PAGE_CONFIG, INDIAN_STATES


class UserInterface:
    def __init__(self):
        self.ai_service = AIService()
        self.route_service = RouteService()
        self.booking_service = BookingService()
        self.auth_service = AuthService()
        self.db = DatabaseService()

    def run(self):
        """Main UI application"""
        st.title(APP_TITLE)
        st.markdown("---")

        # Sidebar for navigation
        page = st.sidebar.selectbox(
            "Choose a page", ["Book a Ride", "My Bookings", "About"]
        )

        if page == "Book a Ride":
            self.render_booking_page()
        elif page == "My Bookings":
            self.render_bookings_page()
        elif page == "About":
            self.render_about_page()

    def render_booking_page(self):
        """Render the main booking page"""
        st.header("🚗 Book Your Ride")

        # Get current user info
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("Please log in to book a ride")
            return

        user = self.auth_service.get_user(user_id)
        if not user:
            st.error("User not found. Please log in again.")
            return

        user_city = user.get("city", "")
        user_state = user.get("state", "")

        # Create two columns for better layout
        col1, col2 = st.columns([2, 1])

        with col1:
            # City selection for origin and destination
            st.subheader("📍 Trip Details")

            # Origin city and place selection
            col_origin_city, col_origin_place = st.columns([1, 2])
            with col_origin_city:
                origin_city = st.selectbox(
                    "Origin City",
                    options=[user_city]
                    + [
                        city
                        for state, cities in INDIAN_STATES.items()
                        for city in cities
                        if city != user_city
                    ],
                    index=0,
                    help="Select the city for pickup location",
                )

            with col_origin_place:
                origin_place = st.text_input(
                    "Pickup Location",
                    placeholder=f"Enter pickup address in {origin_city}",
                    help=f"Enter your pickup location in {origin_city}",
                )

            # Destination city and place selection
            col_dest_city, col_dest_place = st.columns([1, 2])
            with col_dest_city:
                destination_city = st.selectbox(
                    "Destination City",
                    options=[user_city]
                    + [
                        city
                        for state, cities in INDIAN_STATES.items()
                        for city in cities
                        if city != user_city
                    ],
                    index=0,
                    help="Select the city for destination",
                )

            with col_dest_place:
                destination_place = st.text_input(
                    "Drop-off Location",
                    placeholder=f"Enter destination address in {destination_city}",
                    help=f"Enter your destination in {destination_city}",
                )

            # Vehicle type selection
            st.subheader("🚙 Choose Vehicle Type")
            vehicle_type = st.selectbox(
                "Select Vehicle",
                options=list(VEHICLE_TYPES.keys()),
                format_func=lambda x: f"{VEHICLE_TYPES[x]['icon']} {VEHICLE_TYPES[x]['name']} (₹{VEHICLE_TYPES[x]['base_rate_per_km']}/km)",
            )

            # Show vehicle details
            if vehicle_type:
                vehicle = VEHICLE_TYPES[vehicle_type]
                st.info(
                    f"""
                **{vehicle['name']}** {vehicle['icon']}
                - Base Fare: ₹{vehicle['base_fare']}
                - Rate per km: ₹{vehicle['base_rate_per_km']}
                - Capacity: {vehicle['capacity']} passengers
                """
                )

        with col2:
            # City-specific suggestions
            st.subheader(f"🏙️ Popular Places in {user_city}")

            # Initialize session state for suggestions
            if "city_suggestions" not in st.session_state:
                st.session_state.city_suggestions = []
            if "suggestions_loaded" not in st.session_state:
                st.session_state.suggestions_loaded = False

            # Button to refresh suggestions
            if st.button("🔄 Refresh Suggestions", key="refresh_suggestions"):
                st.session_state.suggestions_loaded = False
                st.rerun()

            # Load suggestions if not loaded yet
            if not st.session_state.suggestions_loaded:
                with st.spinner("🔍 Getting AI-powered suggestions..."):
                    try:
                        city_suggestions = self.auth_service.get_city_suggestions(
                            user_city
                        )
                        st.session_state.city_suggestions = city_suggestions
                        st.session_state.suggestions_loaded = True
                    except Exception as e:
                        st.error(f"Failed to load suggestions: {str(e)}")
                        city_suggestions = []
                        st.session_state.city_suggestions = city_suggestions
                        st.session_state.suggestions_loaded = True
            else:
                city_suggestions = st.session_state.city_suggestions

            if city_suggestions:
                st.write("**Quick Suggestions:**")
                for i, place in enumerate(city_suggestions[:8]):  # Show first 8 places
                    if st.button(f"📍 {place}", key=f"origin_suggest_{i}"):
                        st.session_state.origin_place = place
                        st.session_state.origin_city = user_city
                        st.rerun()

                # Add destination suggestions
                st.write("**Destination Suggestions:**")
                for i, place in enumerate(city_suggestions[:8]):  # Show first 8 places
                    if st.button(f"🎯 {place}", key=f"dest_suggest_{i}"):
                        st.session_state.destination_place = place
                        st.session_state.destination_city = user_city
                        st.rerun()
            else:
                st.info(
                    f"Click 'Refresh Suggestions' to get AI-powered place suggestions for {user_city}"
                )

            # Cross-city suggestions
            st.subheader("🌆 Other Cities")
            if st.button(f"🚗 {user_city} to Delhi"):
                st.session_state.origin_city = user_city
                st.session_state.destination_city = "Delhi"
                st.rerun()
            if st.button(f"🚗 {user_city} to Mumbai"):
                st.session_state.origin_city = user_city
                st.session_state.destination_city = "Mumbai"
                st.rerun()
            if st.button(f"🚗 {user_city} to Bangalore"):
                st.session_state.origin_city = user_city
                st.session_state.destination_city = "Bangalore"
                st.rerun()

        # Initialize session state for quick suggestions
        if "origin_place" not in st.session_state:
            st.session_state.origin_place = ""
        if "origin_city" not in st.session_state:
            st.session_state.origin_city = user_city
        if "destination_place" not in st.session_state:
            st.session_state.destination_place = ""
        if "destination_city" not in st.session_state:
            st.session_state.destination_city = user_city

        # Set session state values if quick buttons were clicked
        if st.session_state.origin_place:
            origin_place = st.session_state.origin_place
        if st.session_state.origin_city:
            origin_city = st.session_state.origin_city
        if st.session_state.destination_place:
            destination_place = st.session_state.destination_place
        if st.session_state.destination_city:
            destination_city = st.session_state.destination_city

        # Search for rides button
        if st.button("🔍 Search for Rides", type="primary", use_container_width=True):
            if not origin_place or not destination_place:
                st.error("Please enter both pickup and destination locations")
            elif not origin_city or not destination_city:
                st.error("Please select both origin and destination cities")
            else:
                # Validate places exist in their respective cities using Gemini
                with st.spinner("🔍 Validating places with AI..."):
                    origin_valid = self.auth_service.validate_place_in_city(
                        origin_place, origin_city
                    )
                    destination_valid = self.auth_service.validate_place_in_city(
                        destination_place, destination_city
                    )

                if not origin_valid:
                    st.error(
                        f"❌ Place '{origin_place}' not found in {origin_city}. Please enter a valid location."
                    )
                elif not destination_valid:
                    st.error(
                        f"❌ Place '{destination_place}' not found in {destination_city}. Please enter a valid location."
                    )
                else:
                    # Create full location strings
                    full_origin = f"{origin_place}, {origin_city}"
                    full_destination = f"{destination_place}, {destination_city}"
                    self.process_ride_search(
                        full_origin, full_destination, vehicle_type
                    )

    def process_ride_search(self, origin: str, destination: str, vehicle_type: str):
        """Process ride search and show results"""
        with st.spinner("🔍 Analyzing route and checking conditions..."):
            # Get AI analysis
            conditions = self.ai_service.get_realtime_conditions(origin, destination)

            # Get route suggestions
            route_data = self.route_service.suggest_routes(
                origin, destination, vehicle_type
            )

            # Calculate pricing for each route
            for route in route_data["routes"]:
                pricing = self.route_service.calculate_route_pricing(
                    route, vehicle_type, conditions
                )
                route["pricing"] = pricing

            # Store in session state for admin panel
            st.session_state.route_data = route_data
            st.session_state.conditions = conditions

        # Display results
        self.display_route_results(route_data, conditions)

    def display_route_results(self, route_data: dict, conditions: dict):
        """Display route suggestions and pricing"""
        st.markdown("---")
        st.header("🗺️ Route Options")

        # Show current conditions and real distance
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Weather",
                conditions["weather"].replace("_", " ").title(),
                f"{conditions['weather_multiplier']}x multiplier",
            )
        with col2:
            st.metric(
                "Traffic",
                conditions["traffic"].replace("_", " ").title(),
                f"{conditions['traffic_multiplier']}x multiplier",
            )
        with col3:
            if route_data.get("real_distance_km"):
                st.metric(
                    "Real Distance",
                    f"{route_data['real_distance_km']} km",
                    "GPS calculated",
                )
            else:
                st.metric("Distance", "Calculating...", "Using geocoding")
        with col4:
            if conditions.get("is_demo", False):
                st.warning("Demo Mode - Using simulated data")
            else:
                st.success("Live Data - Real-time conditions")

        # Display route options
        for i, route in enumerate(route_data["routes"], 1):
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    st.subheader(f"Route {i}: {route['name']}")
                    st.write(f"📏 Distance: {route['distance_km']} km")
                    st.write(
                        f"⏱️ Estimated Time: {route['estimated_time_minutes']} minutes"
                    )
                    st.write(f"🚦 Traffic Level: {route['traffic_level'].title()}")
                    st.write(f"ℹ️ {route['description']}")

                    # Display places along route
                    if route.get("places_along_route"):
                        with st.expander(
                            f"📍 Places along Route {i} ({len(route['places_along_route'])} places)"
                        ):
                            for place in route["places_along_route"]:
                                st.write(
                                    f"• **{place['name']}** ({place['type']}) - {place['description']}"
                                )
                                st.write(
                                    f"  📍 {place['distance_from_origin']} km from origin"
                                )

                with col2:
                    pricing = route["pricing"]
                    st.metric("Total Fare", f"₹{pricing['final_fare']}")
                    st.write(f"Base Cost: ₹{pricing['base_cost']}")
                    st.write(f"Driver Gets: ₹{pricing['driver_earnings']}")
                    st.write(f"Company Profit: ₹{pricing['company_profit']}")

                    # Route characteristics
                    if route.get("route_type"):
                        st.write(f"**Route Type:** {route['route_type'].title()}")
                    if route.get("fuel_efficiency"):
                        st.write(
                            f"**Fuel Efficiency:** {route['fuel_efficiency'].title()}"
                        )
                    if route.get("comfort_level"):
                        st.write(
                            f"**Comfort:** {route['comfort_level'].replace('_', ' ').title()}"
                        )

                with col3:
                    if st.button(f"Select Route {i}", key=f"select_route_{i}"):
                        self.confirm_booking(route_data, route, pricing)

        # Show pricing breakdown
        self.show_pricing_breakdown(route_data["routes"][0]["pricing"])

    def show_pricing_breakdown(self, pricing: dict):
        """Show detailed pricing breakdown"""
        st.markdown("---")
        st.subheader("💰 Pricing Breakdown")

        breakdown = pricing["breakdown"]

        # Create a pie chart for fare distribution
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=["Driver Earnings", "Company Profit"],
                    values=[pricing["driver_earnings"], pricing["company_profit"]],
                    hole=0.3,
                )
            ]
        )
        fig.update_layout(title="Fare Distribution")
        st.plotly_chart(fig, use_container_width=True)

        # Show detailed breakdown
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Cost Components:**")
            st.write(f"• Base Fare: ₹{breakdown['base_fare']}")
            st.write(f"• Distance Cost: ₹{breakdown['distance_cost']}")
            st.write(f"• Weather Adjustment: ₹{breakdown['weather_adjustment']}")
            st.write(f"• Traffic Adjustment: ₹{breakdown['traffic_adjustment']}")

        with col2:
            st.write("**Multipliers Applied:**")
            st.write(f"• Weather: {pricing['weather_multiplier']}x")
            st.write(f"• Traffic: {pricing['traffic_multiplier']}x")
            st.write(f"• **Total Fare: ₹{pricing['final_fare']}**")

    def confirm_booking(self, route_data: dict, selected_route: dict, pricing: dict):
        """Confirm booking and create booking record"""
        # Get current user ID
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("User not logged in")
            return

        # Create booking
        booking_data = {
            "user_id": user_id,
            "origin": route_data["origin"],
            "destination": route_data["destination"],
            "vehicle_type": route_data["vehicle_type"],
            "selected_route_id": selected_route["id"],
            "route_name": selected_route["name"],
            "distance_km": selected_route["distance_km"],
            "estimated_time_minutes": selected_route["estimated_time_minutes"],
            "pricing": pricing,
        }

        booking = self.booking_service.create_booking(booking_data)

        st.success(f"✅ Booking Confirmed! Booking ID: {booking['id']}")
        st.balloons()

        # Show booking details
        st.markdown("---")
        st.subheader("📋 Booking Details")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Booking ID:** {booking['id']}")
            st.write(f"**Route:** {booking['origin']} → {booking['destination']}")
            st.write(f"**Vehicle:** {VEHICLE_TYPES[booking['vehicle_type']]['name']}")
            st.write(f"**Distance:** {booking['distance_km']} km")

        with col2:
            st.write(f"**Estimated Time:** {booking['estimated_time_minutes']} minutes")
            st.write(f"**Total Fare:** ₹{pricing['final_fare']}")
            st.write(f"**Driver Earnings:** ₹{pricing['driver_earnings']}")
            st.write(f"**Company Profit:** ₹{pricing['company_profit']}")

    def render_bookings_page(self):
        """Render bookings history page"""
        st.header("📋 My Bookings")

        # Get current user ID
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("Please log in to view your bookings")
            return

        # Get user's bookings from database
        bookings = self.db.get_bookings_by_user(user_id)

        if not bookings:
            st.info("No bookings found. Book your first ride!")
            return

        for booking in bookings:  # Show newest first
            with st.expander(f"Booking {booking['id']} - {booking['status'].title()}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(
                        f"**Route:** {booking['origin']} → {booking['destination']}"
                    )
                    st.write(
                        f"**Vehicle:** {VEHICLE_TYPES[booking['vehicle_type']]['name']}"
                    )
                    st.write(f"**Distance:** {booking['distance_km']} km")
                    st.write(f"**Created:** {booking['created_at']}")

                with col2:
                    if booking.get("pricing"):
                        pricing = booking["pricing"]
                        st.write(f"**Total Fare:** ₹{pricing['final_fare']}")
                        st.write(f"**Driver Gets:** ₹{pricing['driver_earnings']}")
                        st.write(f"**Company Profit:** ₹{pricing['company_profit']}")

                    if booking.get("confirmed_at"):
                        st.write(f"**Confirmed:** {booking['confirmed_at']}")

                if booking["status"] == "pending":
                    if st.button(
                        f"Cancel Booking {booking['id']}", key=f"cancel_{booking['id']}"
                    ):
                        self.booking_service.cancel_booking(booking["id"])
                        st.rerun()

    def render_about_page(self):
        """Render about page"""
        st.header("About India Cab Service")

        st.markdown(
            """
        ### 🚗 Your Reliable Ride Partner
        
        India Cab Service is an AI-powered ride booking platform that provides:
        
        - **Smart Route Planning**: AI analyzes traffic and weather conditions
        - **Multiple Vehicle Options**: Bike, Car, Premium, and 6-Seater options
        - **Transparent Pricing**: See exactly how your fare is calculated
        - **Real-time Updates**: Live traffic and weather data integration
        
        ### 🛠️ Technology Stack
        
        - **AI Analysis**: Google Gemini API for real-time conditions
        - **Route Optimization**: Smart algorithms for best routes
        - **Transparent Pricing**: Clear breakdown of all costs
        - **Admin Dashboard**: Complete business analytics
        
        ### 📊 Features
        
        - Real-time weather and traffic analysis
        - Multiple route suggestions with different traffic levels
        - Transparent pricing with driver and company profit breakdown
        - Admin panel for business management
        - Booking history and analytics
        """
        )

        st.markdown("---")
        st.write("**Developed with ❤️ for India's transportation needs**")
