import pytest
import sqlite3
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
tmp_db.close()

import app as airgo
airgo.DATABASE = tmp_db.name


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    airgo.init_db()
    yield
    os.unlink(tmp_db.name)


@pytest.fixture
def app():
    airgo.app.config["TESTING"] = True
    airgo.app.secret_key = "test_key"
    return airgo.app


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


@pytest.fixture
def logged_in(app):
    with app.test_client() as c:
        c.post("/signup", data={
            "full_name": "Test User",
            "email": "student@test.com",
            "password": "password123"
        })
        c.post("/login", data={
            "email": "student@test.com",
            "password": "password123"
        })
    yield c
    conn = airgo.get_db_connection()
    conn.execute("DELETE FROM bookings WHERE email = ?", ("student@test.com",))
    conn.execute("DELETE FROM users WHERE email = ?", ("student@test.com",))
    conn.commit()
    conn.close()


def get_user_id(email):
    conn = airgo.get_db_connection()
    row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return row["id"] if row else None


def make_booking(user_id, reference="TESTREF1", seat="3A"):
    conn = airgo.get_db_connection()
    conn.execute("""
        INSERT OR IGNORE INTO bookings (
            user_id, booking_reference, first_name, last_name, email,
            phone, passport_number, airline, departure_airport,
            departure_city, departure_code, destination_airport,
            destination_city, destination_code, flight_date,
            departure_time, arrival_time, ticket_class, meal_choice,
            seat, price, points_earned, trip_type, change_request,
            change_status, flight_status, extra_baggage,
            priority_boarding, wifi_package, lounge_access,
            requested_route, requested_date
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        user_id, reference, "Test", "Passenger", "student@test.com",
        "07700900000", "AB123456", "AirGo", "London Heathrow",
        "London", "LHR", "Paris Charles de Gaulle", "Paris", "CDG",
        "2025-08-01", "08:00", "10:15", "Economy", "Standard Meal",
        seat, 120.0, 600, "return", "", "None", "Scheduled",
        0, 0, 0, 0, "", ""
    ))
    conn.commit()
    conn.close()


def get_booking_id(reference):
    conn = airgo.get_db_connection()
    row = conn.execute("SELECT id FROM bookings WHERE booking_reference = ?", (reference,)).fetchone()
    conn.close()
    return row["id"] if row else None


def get_booking_count(user_id):
    conn = airgo.get_db_connection()
    row = conn.execute("SELECT COUNT(*) as cnt FROM bookings WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row["cnt"]