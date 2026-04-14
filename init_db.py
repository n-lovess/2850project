#!/usr/bin/env python3
import os
import sqlite3
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "bookings.db")


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_db_connection()

    print("Creating tables...")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            booking_reference TEXT NOT NULL UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            passport_number TEXT NOT NULL,
            airline TEXT NOT NULL,
            departure_airport TEXT NOT NULL,
            departure_city TEXT NOT NULL,
            departure_code TEXT NOT NULL,
            destination_airport TEXT NOT NULL,
            destination_city TEXT NOT NULL,
            destination_code TEXT NOT NULL,
            flight_date TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            arrival_time TEXT NOT NULL,
            ticket_class TEXT NOT NULL,
            meal_choice TEXT NOT NULL,
            seat TEXT NOT NULL,
            price REAL NOT NULL,
            points_earned INTEGER NOT NULL DEFAULT 0,
            trip_type TEXT NOT NULL DEFAULT 'return',
            change_request TEXT,
            change_status TEXT NOT NULL DEFAULT 'None',
            flight_status TEXT NOT NULL DEFAULT 'Scheduled',
            extra_baggage INTEGER NOT NULL DEFAULT 0,
            priority_boarding INTEGER NOT NULL DEFAULT 0,
            wifi_package INTEGER NOT NULL DEFAULT 0,
            lounge_access INTEGER NOT NULL DEFAULT 0,
            requested_route TEXT DEFAULT '',
            requested_date TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            airline TEXT NOT NULL,
            departure_airport TEXT NOT NULL,
            departure_city TEXT NOT NULL,
            departure_code TEXT NOT NULL,
            destination_airport TEXT NOT NULL,
            destination_city TEXT NOT NULL,
            destination_code TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            arrival_time TEXT NOT NULL,
            base_price REAL NOT NULL,
            ticket_class TEXT NOT NULL,
            seats_left INTEGER NOT NULL DEFAULT 0
        )
    """)

    admin_email = "admin@airgo.com"
    existing_admin = conn.execute(
        "SELECT id FROM users WHERE email = ?",
        (admin_email,)
    ).fetchone()

    if not existing_admin:
        print("Creating admin user...")
        conn.execute("""
            INSERT INTO users (full_name, email, password_hash)
            VALUES (?, ?, ?)
        """, (
            "AirGo Admin",
            admin_email,
            generate_password_hash("admin123")
        ))

    # Seed flights
    flight_count = conn.execute("SELECT COUNT(*) as cnt FROM flights").fetchone()["cnt"]
    if flight_count == 0:
        print("Seeding flights data...")
        conn.executemany("""
            INSERT INTO flights (
                airline, departure_airport, departure_city, departure_code,
                destination_airport, destination_city, destination_code,
                departure_time, arrival_time, base_price, ticket_class, seats_left
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            ("AirGo", "London Heathrow", "London", "LHR", "Paris Charles de Gaulle", "Paris", "CDG", "08:00", "10:15", 120, "Economy", 14),
            ("AirGo", "London Gatwick", "London", "LGW", "Paris Orly", "Paris", "ORY", "12:30", "14:45", 185, "Premium Economy", 7),
            ("AirGo", "London Stansted", "London", "STN", "Dubai International", "Dubai", "DXB", "18:20", "03:35", 310, "Business", 3),
            ("AirGo", "Paris Charles de Gaulle", "Paris", "CDG", "Dubai International", "Dubai", "DXB", "09:45", "18:10", 275, "Economy", 11),
            ("AirGo", "Dubai International", "Dubai", "DXB", "London Heathrow", "London", "LHR", "14:00", "18:45", 420, "Business", 5),
            ("AirGo", "London City", "London", "LCY", "John F. Kennedy", "New York", "JFK", "10:00", "13:25", 510, "Premium Economy", 8),
        ])

    # Add indexes
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_bookings_reference ON bookings(booking_reference)")

    conn.commit()
    conn.close()
    print("\nDatabase initialization completed successfully!")
    print("- Created tables: users, bookings, flights")
    print("- Admin user: admin@airgo.com / admin123")
    print("- 6 sample flights inserted")
    print("- Indexes created for performance")


if __name__ == "__main__":
    init_database()