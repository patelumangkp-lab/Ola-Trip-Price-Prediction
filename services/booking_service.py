"""
Booking Service for managing ride bookings and admin operations
"""

from datetime import datetime
from typing import Dict, List, Optional
from services.database_service import DatabaseService


class BookingService:
    def __init__(self):
        self.db = DatabaseService()

    def create_booking(self, booking_data: Dict) -> Dict:
        """
        Create a new booking

        Args:
            booking_data (dict): Booking information

        Returns:
            dict: Created booking with ID and timestamp
        """
        booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"

        booking = {
            "id": booking_id,
            "user_id": booking_data.get("user_id", ""),
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "selected_route_id": None,
            **booking_data,
        }

        # Save to database
        self.db.create_booking(booking)

        return booking

    def select_route(self, booking_id: str, route_id: str, pricing: Dict) -> bool:
        """
        Select a route for a booking and update admin data

        Args:
            booking_id (str): Booking ID
            route_id (str): Selected route ID
            pricing (dict): Pricing information

        Returns:
            bool: Success status
        """
        booking = self.get_booking(booking_id)
        if not booking:
            return False

        # Update booking
        updates = {
            "selected_route_id": route_id,
            "status": "confirmed",
            "pricing": pricing,
            "confirmed_at": datetime.now().isoformat(),
        }

        success = self.db.update_booking(booking_id, updates)
        if not success:
            return False

        # Update admin data
        admin_data = self.db.get_admin_data()

        # Calculate new totals
        new_total_bookings = admin_data["total_bookings"] + 1
        new_total_revenue = admin_data["total_revenue"] + pricing["final_fare"]
        new_total_driver_earnings = (
            admin_data["total_driver_earnings"] + pricing["driver_earnings"]
        )
        new_total_company_profit = (
            admin_data["total_company_profit"] + pricing["company_profit"]
        )

        # Update route statistics
        route_key = f"{booking['origin']}_to_{booking['destination']}"
        route_stats = admin_data.get("route_statistics", {})

        if route_key not in route_stats:
            route_stats[route_key] = {
                "total_bookings": 0,
                "total_revenue": 0.0,
                "average_fare": 0.0,
            }

        route_stats[route_key]["total_bookings"] += 1
        route_stats[route_key]["total_revenue"] += pricing["final_fare"]
        route_stats[route_key]["average_fare"] = (
            route_stats[route_key]["total_revenue"]
            / route_stats[route_key]["total_bookings"]
        )

        # Update admin data
        admin_updates = {
            "total_bookings": new_total_bookings,
            "total_revenue": new_total_revenue,
            "total_driver_earnings": new_total_driver_earnings,
            "total_company_profit": new_total_company_profit,
            "route_statistics": route_stats,
        }

        self.db.update_admin_data(admin_updates)

        return True

    def get_booking(self, booking_id: str) -> Optional[Dict]:
        """Get booking by ID"""
        return self.db.get_booking_by_id(booking_id)

    def get_all_bookings(self) -> List[Dict]:
        """Get all bookings"""
        return self.db.get_all_bookings()

    def get_admin_dashboard_data(self) -> Dict:
        """Get data for admin dashboard"""
        recent_bookings = self.db.get_recent_bookings(10)
        admin_data = self.db.get_admin_data()
        pending_count = self.db.get_pending_bookings_count()

        return {
            "summary": admin_data,
            "recent_bookings": recent_bookings,
            "total_pending_bookings": pending_count,
        }

    def get_route_analytics(self) -> Dict:
        """Get route analytics for admin"""
        admin_data = self.db.get_admin_data()
        route_stats = admin_data.get("route_statistics", {})

        # Sort routes by revenue
        sorted_routes = sorted(
            route_stats.items(), key=lambda x: x[1]["total_revenue"], reverse=True
        )

        return {"top_routes": sorted_routes[:5], "all_routes": route_stats}

    def cancel_booking(self, booking_id: str) -> bool:
        """Cancel a booking"""
        updates = {"status": "cancelled", "cancelled_at": datetime.now().isoformat()}
        return self.db.update_booking(booking_id, updates)
