"""
Database Service for SQLite operations
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import json


class DatabaseService:
    def __init__(self, db_path: str = "main.db"):
        self.db_path = db_path
        self._ensure_database_exists()
        self._create_tables()

    def _ensure_database_exists(self):
        """Ensure database file exists"""
        os.makedirs(
            os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".",
            exist_ok=True,
        )

    def _create_tables(self):
        """Create all necessary tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    password_hash TEXT,
                    state TEXT,
                    city TEXT,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Admins table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    email TEXT NOT NULL,
                    name TEXT NOT NULL,
                    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_super_admin BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """
            )

            # Bookings table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS bookings (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    origin TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    vehicle_type TEXT NOT NULL,
                    selected_route_id TEXT,
                    route_name TEXT,
                    distance_km REAL,
                    estimated_time_minutes INTEGER,
                    pricing TEXT,  -- JSON string
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confirmed_at TIMESTAMP,
                    cancelled_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """
            )

            # Admin data table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS admin_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_bookings INTEGER DEFAULT 0,
                    total_revenue REAL DEFAULT 0.0,
                    total_driver_earnings REAL DEFAULT 0.0,
                    total_company_profit REAL DEFAULT 0.0,
                    route_statistics TEXT,  -- JSON string
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Initialize admin data if not exists
            cursor.execute("SELECT COUNT(*) FROM admin_data")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    """
                    INSERT INTO admin_data (total_bookings, total_revenue, total_driver_earnings, total_company_profit, route_statistics)
                    VALUES (0, 0.0, 0.0, 0.0, '{}')
                """
                )

            conn.commit()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute SELECT query and return results as list of dictionaries"""
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT query and return last row ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    # User operations
    def create_user(self, user_data: Dict) -> str:
        """Create a new user"""
        query = """
            INSERT INTO users (id, name, email, phone, password_hash, state, city, is_admin, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            user_data["id"],
            user_data["name"],
            user_data["email"],
            user_data.get("phone", ""),
            user_data.get("password_hash", ""),
            user_data.get("state", ""),
            user_data.get("city", ""),
            user_data.get("is_admin", False),
            user_data.get("created_at", datetime.now().isoformat()),
        )
        self.execute_update(query, params)
        return user_data["id"]

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = ?"
        results = self.execute_query(query, (user_id,))
        return results[0] if results else None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = ?"
        results = self.execute_query(query, (email,))
        return results[0] if results else None

    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        query = "SELECT * FROM users ORDER BY created_at DESC"
        return self.execute_query(query)

    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Update user data"""
        set_clauses = []
        params = []

        for key, value in updates.items():
            set_clauses.append(f"{key} = ?")
            params.append(value)

        if not set_clauses:
            return False

        params.append(user_id)
        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?"

        return self.execute_update(query, tuple(params)) > 0

    # Admin operations
    def create_admin(self, admin_data: Dict) -> int:
        """Create admin record"""
        query = """
            INSERT INTO admins (user_id, email, name, granted_at, is_super_admin)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            admin_data["user_id"],
            admin_data["email"],
            admin_data["name"],
            admin_data.get("granted_at", datetime.now().isoformat()),
            admin_data.get("is_super_admin", False),
        )
        return self.execute_insert(query, params)

    def get_all_admins(self) -> List[Dict]:
        """Get all admins"""
        query = "SELECT * FROM admins ORDER BY granted_at DESC"
        return self.execute_query(query)

    def is_admin(self, user_id: str) -> bool:
        """Check if user is admin"""
        query = "SELECT COUNT(*) as count FROM admins WHERE user_id = ?"
        results = self.execute_query(query, (user_id,))
        return results[0]["count"] > 0 if results else False

    # Booking operations
    def create_booking(self, booking_data: Dict) -> str:
        """Create a new booking"""
        query = """
            INSERT INTO bookings (id, user_id, origin, destination, vehicle_type, selected_route_id, 
                                route_name, distance_km, estimated_time_minutes, pricing, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            booking_data["id"],
            booking_data["user_id"],
            booking_data["origin"],
            booking_data["destination"],
            booking_data["vehicle_type"],
            booking_data.get("selected_route_id"),
            booking_data.get("route_name"),
            booking_data.get("distance_km"),
            booking_data.get("estimated_time_minutes"),
            json.dumps(booking_data.get("pricing", {})),
            booking_data.get("status", "pending"),
            booking_data.get("created_at", datetime.now().isoformat()),
        )
        self.execute_update(query, params)
        return booking_data["id"]

    def get_booking_by_id(self, booking_id: str) -> Optional[Dict]:
        """Get booking by ID"""
        query = "SELECT * FROM bookings WHERE id = ?"
        results = self.execute_query(query, (booking_id,))
        if results:
            booking = results[0]
            # Parse JSON fields
            if booking["pricing"]:
                booking["pricing"] = json.loads(booking["pricing"])
            return booking
        return None

    def get_all_bookings(self) -> List[Dict]:
        """Get all bookings"""
        query = "SELECT * FROM bookings ORDER BY created_at DESC"
        results = self.execute_query(query)
        # Parse JSON fields
        for booking in results:
            if booking["pricing"]:
                booking["pricing"] = json.loads(booking["pricing"])
        return results

    def get_bookings_by_user(self, user_id: str) -> List[Dict]:
        """Get bookings for a specific user"""
        query = "SELECT * FROM bookings WHERE user_id = ? ORDER BY created_at DESC"
        results = self.execute_query(query, (user_id,))
        # Parse JSON fields
        for booking in results:
            if booking["pricing"]:
                booking["pricing"] = json.loads(booking["pricing"])
        return results

    def update_booking(self, booking_id: str, updates: Dict) -> bool:
        """Update booking data"""
        set_clauses = []
        params = []

        for key, value in updates.items():
            if key == "pricing" and isinstance(value, dict):
                value = json.dumps(value)
            set_clauses.append(f"{key} = ?")
            params.append(value)

        if not set_clauses:
            return False

        params.append(booking_id)
        query = f"UPDATE bookings SET {', '.join(set_clauses)} WHERE id = ?"

        return self.execute_update(query, tuple(params)) > 0

    # Admin data operations
    def get_admin_data(self) -> Dict:
        """Get admin dashboard data"""
        query = "SELECT * FROM admin_data ORDER BY updated_at DESC LIMIT 1"
        results = self.execute_query(query)
        if results:
            data = results[0]
            # Parse JSON fields
            if data["route_statistics"]:
                data["route_statistics"] = json.loads(data["route_statistics"])
            return data
        return {
            "total_bookings": 0,
            "total_revenue": 0.0,
            "total_driver_earnings": 0.0,
            "total_company_profit": 0.0,
            "route_statistics": {},
        }

    def update_admin_data(self, updates: Dict) -> bool:
        """Update admin data"""
        set_clauses = []
        params = []

        for key, value in updates.items():
            if key == "route_statistics" and isinstance(value, dict):
                value = json.dumps(value)
            set_clauses.append(f"{key} = ?")
            params.append(value)

        if not set_clauses:
            return False

        params.append(datetime.now().isoformat())
        set_clauses.append("updated_at = ?")

        query = f"UPDATE admin_data SET {', '.join(set_clauses)}"

        return self.execute_update(query, tuple(params)) > 0

    def get_recent_bookings(self, limit: int = 10) -> List[Dict]:
        """Get recent confirmed bookings"""
        query = """
            SELECT b.*, u.name as user_name, u.email as user_email
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            WHERE b.status = 'confirmed'
            ORDER BY b.confirmed_at DESC
            LIMIT ?
        """
        results = self.execute_query(query, (limit,))
        # Parse JSON fields
        for booking in results:
            if booking["pricing"]:
                booking["pricing"] = json.loads(booking["pricing"])
        return results

    def get_pending_bookings_count(self) -> int:
        """Get count of pending bookings"""
        query = "SELECT COUNT(*) as count FROM bookings WHERE status = 'pending'"
        results = self.execute_query(query)
        return results[0]["count"] if results else 0

    def close(self):
        """Close database connection (if needed)"""
        pass
