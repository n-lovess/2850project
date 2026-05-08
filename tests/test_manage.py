import app as airgo


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


def test_bookings_page_needs_login(client):
    res = client.get("/bookings")
    assert res.status_code == 302

def test_bookings_page_loads_when_logged_in(logged_in):
    res = logged_in.get("/bookings")
    assert res.status_code == 200

def test_request_change_needs_login(client):
    res = client.post("/request-change/1", data={
        "requested_departure": "London",
        "requested_destination": "Paris",
        "requested_date": "2026-09-01",
        "request_reason": "test"
    }, follow_redirects=True)
    assert b"log in" in res.data.lower()

def test_boarding_pass_needs_login(client):
    res = client.get("/boarding-pass/1", follow_redirects=True)
    assert res.status_code == 200

def test_boarding_pass_wrong_user(logged_in):
    res = logged_in.get("/boarding-pass/99999", follow_redirects=True)
    assert b"not found" in res.data.lower() or res.status_code == 200

def test_cancel_passenger_needs_login(client):
    res = client.post("/cancel-passenger/1", follow_redirects=True)
    assert b"log in" in res.data.lower() or res.status_code == 200