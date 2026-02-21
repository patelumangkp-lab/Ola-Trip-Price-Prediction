"""
Streamlit Admin Interface for Cab Service Management
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict

from services.booking_service import BookingService
from services.route_service import RouteService
from services.ai_service import AIService
from services.database_service import DatabaseService
from config import VEHICLE_TYPES


class AdminInterface:
    def __init__(self):
        self.booking_service = BookingService()
        self.route_service = RouteService()
        self.ai_service = AIService()
        self.db = DatabaseService()

    def run(self):
        """Main admin interface"""
        # Check if user is admin (authentication handled in main.py)
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("Please log in to access admin panel")
            return

        from services.auth_service import AuthService

        auth_service = AuthService()

        if not auth_service.is_admin(user_id):
            st.error("You don't have admin access")
            return

        st.title("👨‍💼 Admin Dashboard")
        st.markdown("---")

        # Sidebar navigation
        page = st.sidebar.selectbox(
            "Admin Panel",
            [
                "Dashboard Overview",
                "Route Management",
                "Booking Management",
                "User Management",
                "Analytics",
                "Settings",
            ],
        )

        if page == "Dashboard Overview":
            self.render_dashboard_overview()
        elif page == "Route Management":
            self.render_route_management()
        elif page == "Booking Management":
            self.render_booking_management()
        elif page == "User Management":
            self.render_user_management()
        elif page == "Analytics":
            self.render_analytics()
        elif page == "Settings":
            self.render_settings()

    def render_user_management(self):
        """Render user management page"""
        st.header("👥 User Management")

        from services.auth_service import AuthService

        auth_service = AuthService()

        # Get all users
        users = auth_service.get_all_users()
        admins = auth_service.get_all_admins()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 User Statistics")
            st.metric("Total Users", len(users))
            st.metric("Total Admins", len(admins))
            st.metric("Regular Users", len(users) - len(admins))

        with col2:
            st.subheader("👑 Admin Users")
            for admin in admins:
                st.write(
                    f"• {admin.get('name', 'Unknown')} ({admin.get('email', 'No email')})"
                )
                if admin.get("is_super_admin"):
                    st.write("  🏆 Super Admin (First User)")

        st.markdown("---")

        # User list
        st.subheader("📋 All Users")
        if users:
            user_data = []
            for user in users:
                user_data.append(
                    {
                        "ID": user["id"],
                        "Name": user.get("name", "Unknown"),
                        "Email": user.get("email", "No email"),
                        "City": user.get("city", "Unknown"),
                        "State": user.get("state", "Unknown"),
                        "Admin": "Yes" if user.get("is_admin") else "No",
                        "Joined": user.get("created_at", "Unknown")[:10],
                    }
                )

            import pandas as pd

            df = pd.DataFrame(user_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users found")

    def render_dashboard_overview(self):
        """Render main dashboard overview"""
        st.header("📊 Dashboard Overview")

        # Add refresh button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Refresh Data", key="refresh_dashboard"):
                st.rerun()

        # Get admin data
        admin_data = self.booking_service.get_admin_dashboard_data()
        summary = admin_data["summary"]

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Bookings",
                summary["total_bookings"],
                delta=f"+{len([b for b in admin_data['recent_bookings'] if self.is_today(b.get('confirmed_at', ''))])} today",
            )

        with col2:
            st.metric(
                "Total Revenue",
                f"₹{summary['total_revenue']:,.2f}",
                delta=f"₹{summary['total_company_profit']:,.2f} profit",
            )

        with col3:
            st.metric(
                "Driver Earnings",
                f"₹{summary['total_driver_earnings']:,.2f}",
                delta=f"{summary['total_driver_earnings']/max(summary['total_revenue'], 1)*100:.1f}% of revenue",
            )

        with col4:
            st.metric(
                "Company Profit",
                f"₹{summary['total_company_profit']:,.2f}",
                delta=f"{summary['total_company_profit']/max(summary['total_revenue'], 1)*100:.1f}% margin",
            )

        st.markdown("---")

        # Recent bookings
        st.subheader("📋 Recent Bookings")
        recent_bookings = admin_data["recent_bookings"]

        if recent_bookings:
            # Create DataFrame for better display
            booking_data = []
            for booking in recent_bookings:
                booking_data.append(
                    {
                        "ID": booking["id"],
                        "Route": f"{booking['origin']} → {booking['destination']}",
                        "Vehicle": VEHICLE_TYPES[booking["vehicle_type"]]["name"],
                        "Distance": f"{booking['distance_km']} km",
                        "Fare": f"₹{booking['pricing']['final_fare']}",
                        "Driver": f"₹{booking['pricing']['driver_earnings']}",
                        "Profit": f"₹{booking['pricing']['company_profit']}",
                        "Status": booking["status"].title(),
                        "Confirmed": booking.get("confirmed_at", "N/A")[:10],
                    }
                )

            df = pd.DataFrame(booking_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No bookings found")

        # Revenue chart
        self.render_revenue_chart()

    def render_revenue_chart(self):
        """Render revenue analytics chart"""
        st.subheader("💰 Revenue Analytics")

        # Get booking data for chart
        bookings = self.booking_service.get_all_bookings()
        confirmed_bookings = [b for b in bookings if b.get("status") == "confirmed"]

        if confirmed_bookings:
            # Group by date
            daily_revenue = {}
            for booking in confirmed_bookings:
                date = booking.get("confirmed_at", "")[:10]
                if date:
                    if date not in daily_revenue:
                        daily_revenue[date] = {"revenue": 0, "profit": 0, "driver": 0}
                    daily_revenue[date]["revenue"] += booking["pricing"]["final_fare"]
                    daily_revenue[date]["profit"] += booking["pricing"][
                        "company_profit"
                    ]
                    daily_revenue[date]["driver"] += booking["pricing"][
                        "driver_earnings"
                    ]

            # Create chart
            dates = sorted(daily_revenue.keys())
            revenue_data = [daily_revenue[date]["revenue"] for date in dates]
            profit_data = [daily_revenue[date]["profit"] for date in dates]
            driver_data = [daily_revenue[date]["driver"] for date in dates]

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=revenue_data,
                    name="Total Revenue",
                    line=dict(color="blue"),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=profit_data,
                    name="Company Profit",
                    line=dict(color="green"),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=driver_data,
                    name="Driver Earnings",
                    line=dict(color="orange"),
                )
            )

            fig.update_layout(
                title="Daily Revenue Breakdown",
                xaxis_title="Date",
                yaxis_title="Amount (₹)",
                hovermode="x unified",
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No revenue data available")

    def render_route_management(self):
        """Render route management page"""
        st.header("🗺️ Route Management")

        # Route analytics
        route_analytics = self.booking_service.get_route_analytics()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Top Performing Routes")
            top_routes = route_analytics["top_routes"]

            if top_routes:
                route_data = []
                for route, stats in top_routes:
                    route_data.append(
                        {
                            "Route": route.replace("_", " → "),
                            "Bookings": stats["total_bookings"],
                            "Revenue": f"₹{stats['total_revenue']:,.2f}",
                            "Avg Fare": f"₹{stats['average_fare']:,.2f}",
                        }
                    )

                df = pd.DataFrame(route_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No route data available")

        with col2:
            st.subheader("📊 Route Performance Chart")
            if top_routes:
                routes = [route.replace("_", " → ") for route, _ in top_routes]
                revenues = [stats["total_revenue"] for _, stats in top_routes]

                fig = px.bar(
                    x=routes,
                    y=revenues,
                    title="Revenue by Route",
                    labels={"x": "Route", "y": "Revenue (₹)"},
                )
                fig.update_xaxis(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data for chart")

        # Manual route analysis
        st.subheader("🔍 Manual Route Analysis")

        col1, col2 = st.columns(2)
        with col1:
            origin = st.text_input("Origin", placeholder="Enter origin city")
        with col2:
            destination = st.text_input(
                "Destination", placeholder="Enter destination city"
            )

        vehicle_type = st.selectbox("Vehicle Type", list(VEHICLE_TYPES.keys()))

        if st.button("Analyze Route"):
            if origin and destination:
                self.analyze_route(origin, destination, vehicle_type)
            else:
                st.error("Please enter both origin and destination")

    def analyze_route(self, origin: str, destination: str, vehicle_type: str):
        """Analyze a specific route"""
        with st.spinner("Analyzing route..."):
            # Get conditions
            conditions = self.ai_service.get_realtime_conditions(origin, destination)

            # Get routes
            route_data = self.route_service.suggest_routes(
                origin, destination, vehicle_type
            )

            # Calculate pricing
            for route in route_data["routes"]:
                pricing = self.route_service.calculate_route_pricing(
                    route, vehicle_type, conditions
                )
                route["pricing"] = pricing

        st.subheader("Route Analysis Results")

        for i, route in enumerate(route_data["routes"], 1):
            with st.expander(f"Route {i}: {route['name']}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Distance:** {route['distance_km']} km")
                    st.write(f"**Time:** {route['estimated_time_minutes']} minutes")
                    st.write(f"**Traffic:** {route['traffic_level'].title()}")

                    # Show places along route
                    if route.get("places_along_route"):
                        st.write(
                            f"**Places along route:** {len(route['places_along_route'])}"
                        )
                        for place in route["places_along_route"][:3]:  # Show first 3
                            st.write(f"• {place['name']} ({place['type']})")

                with col2:
                    pricing = route["pricing"]
                    st.write(f"**Total Fare:** ₹{pricing['final_fare']}")
                    st.write(f"**Driver Gets:** ₹{pricing['driver_earnings']}")
                    st.write(f"**Company Profit:** ₹{pricing['company_profit']}")

                    # Route characteristics
                    if route.get("route_type"):
                        st.write(f"**Type:** {route['route_type'].title()}")
                    if route.get("fuel_efficiency"):
                        st.write(f"**Fuel:** {route['fuel_efficiency'].title()}")

    def render_booking_management(self):
        """Render booking management page"""
        st.header("📋 Booking Management")

        bookings = self.booking_service.get_all_bookings()

        # Filter options
        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.selectbox(
                "Filter by Status", ["All", "pending", "confirmed", "cancelled"]
            )
        with col2:
            vehicle_filter = st.selectbox(
                "Filter by Vehicle", ["All"] + list(VEHICLE_TYPES.keys())
            )
        with col3:
            if st.button("Refresh Data"):
                st.rerun()

        # Filter bookings
        filtered_bookings = bookings
        if status_filter != "All":
            filtered_bookings = [
                b for b in filtered_bookings if b["status"] == status_filter
            ]
        if vehicle_filter != "All":
            filtered_bookings = [
                b for b in filtered_bookings if b["vehicle_type"] == vehicle_filter
            ]

        # Display bookings
        if filtered_bookings:
            for booking in reversed(filtered_bookings):
                with st.expander(
                    f"Booking {booking['id']} - {booking['status'].title()}"
                ):
                    col1, col2, col3 = st.columns(3)

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
                            st.write(
                                f"**Company Profit:** ₹{pricing['company_profit']}"
                            )

                    with col3:
                        st.write(f"**Status:** {booking['status'].title()}")
                        if booking.get("confirmed_at"):
                            st.write(f"**Confirmed:** {booking['confirmed_at']}")

                        if booking["status"] == "pending":
                            if st.button(
                                f"Confirm Booking {booking['id']}",
                                key=f"confirm_{booking['id']}",
                            ):
                                self.confirm_pending_booking(booking)
        else:
            st.info("No bookings found with current filters")

    def render_analytics(self):
        """Render analytics page"""
        st.header("📊 Advanced Analytics")

        # Vehicle type analytics
        st.subheader("🚗 Vehicle Type Performance")

        bookings = self.booking_service.get_all_bookings()
        confirmed_bookings = [b for b in bookings if b.get("status") == "confirmed"]

        if confirmed_bookings:
            # Group by vehicle type
            vehicle_stats = {}
            for booking in confirmed_bookings:
                vehicle_type = booking["vehicle_type"]
                if vehicle_type not in vehicle_stats:
                    vehicle_stats[vehicle_type] = {
                        "bookings": 0,
                        "revenue": 0,
                        "profit": 0,
                    }

                vehicle_stats[vehicle_type]["bookings"] += 1
                vehicle_stats[vehicle_type]["revenue"] += booking["pricing"][
                    "final_fare"
                ]
                vehicle_stats[vehicle_type]["profit"] += booking["pricing"][
                    "company_profit"
                ]

            # Create charts
            col1, col2 = st.columns(2)

            with col1:
                vehicle_names = [
                    VEHICLE_TYPES[vt]["name"] for vt in vehicle_stats.keys()
                ]
                booking_counts = [stats["bookings"] for stats in vehicle_stats.values()]

                fig = px.pie(
                    values=booking_counts,
                    names=vehicle_names,
                    title="Bookings by Vehicle Type",
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                revenues = [stats["revenue"] for stats in vehicle_stats.values()]

                fig = px.bar(
                    x=vehicle_names,
                    y=revenues,
                    title="Revenue by Vehicle Type",
                    labels={"x": "Vehicle Type", "y": "Revenue (₹)"},
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No analytics data available")

    def render_settings(self):
        """Render settings page"""
        st.header("⚙️ Settings")

        st.subheader("Vehicle Configuration")

        for vehicle_type, config in VEHICLE_TYPES.items():
            with st.expander(f"{config['icon']} {config['name']}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Base Fare:** ₹{config['base_fare']}")
                    st.write(f"**Rate per km:** ₹{config['base_rate_per_km']}")

                with col2:
                    st.write(f"**Capacity:** {config['capacity']} passengers")
                    st.write(f"**Icon:** {config['icon']}")

        st.subheader("System Information")
        st.write(f"**Total Bookings:** {len(self.booking_service.get_all_bookings())}")
        st.write(
            f"**AI Service Status:** {'Active' if self.ai_service.client else 'Demo Mode'}"
        )
        st.write(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def confirm_pending_booking(self, booking: Dict):
        """Confirm a pending booking with route selection"""
        st.subheader(f"Confirm Booking {booking['id']}")

        # Get route suggestions
        with st.spinner("Getting route options..."):
            conditions = self.ai_service.get_realtime_conditions(
                booking["origin"], booking["destination"]
            )
            route_data = self.route_service.suggest_routes(
                booking["origin"], booking["destination"], booking["vehicle_type"]
            )

            # Calculate pricing for each route
            for route in route_data["routes"]:
                pricing = self.route_service.calculate_route_pricing(
                    route, booking["vehicle_type"], conditions
                )
                route["pricing"] = pricing

        # Display route options
        st.write("**Select a route for this booking:**")

        for i, route in enumerate(route_data["routes"], 1):
            with st.expander(f"Route {i}: {route['name']}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Distance:** {route['distance_km']} km")
                    st.write(f"**Time:** {route['estimated_time_minutes']} minutes")
                    st.write(f"**Traffic:** {route['traffic_level'].title()}")

                    # Show places along route
                    if route.get("places_along_route"):
                        st.write(
                            f"**Places along route:** {len(route['places_along_route'])}"
                        )
                        for place in route["places_along_route"][:3]:  # Show first 3
                            st.write(f"• {place['name']} ({place['type']})")

                with col2:
                    pricing = route["pricing"]
                    st.write(f"**Total Fare:** ₹{pricing['final_fare']}")
                    st.write(f"**Driver Gets:** ₹{pricing['driver_earnings']}")
                    st.write(f"**Company Profit:** ₹{pricing['company_profit']}")

                    # Route characteristics
                    if route.get("route_type"):
                        st.write(f"**Type:** {route['route_type'].title()}")
                    if route.get("fuel_efficiency"):
                        st.write(f"**Fuel:** {route['fuel_efficiency'].title()}")

                if st.button(
                    f"Select Route {i}", key=f"select_route_{booking['id']}_{i}"
                ):
                    # Confirm booking with selected route
                    success = self.booking_service.select_route(
                        booking["id"], route["id"], pricing
                    )

                    if success:
                        st.success(f"Booking {booking['id']} confirmed with Route {i}!")
                        st.rerun()
                    else:
                        st.error("Failed to confirm booking. Please try again.")

    def is_today(self, date_string: str) -> bool:
        """Check if date string is today"""
        if not date_string:
            return False
        try:
            date_obj = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
            return date_obj.date() == datetime.now().date()
        except:
            return False
