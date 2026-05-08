
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

import app as airgo


def test_home_loads(client):
    res = client.get("/")
    assert res.status_code == 200

def test_login_page_loads(client):
    res = client.get("/login")
    assert res.status_code == 200

def test_signup_page_loads(client):
    res = client.get("/signup")
    assert res.status_code == 200

def test_forgot_password_page_loads(client):
    res = client.get("/forgot-password")
    assert res.status_code == 200

def test_home_has_airgo_branding(client):
    res = client.get("/")
    assert b"AirGo" in res.data

def test_signup_works(client):
    res = client.post("/signup", data={
        "full_name": "Jane Smith",
        "email": "jane_unique99@test.com",
        "password": "pass123"
    }, follow_redirects=True)
    assert res.status_code == 200
    conn = airgo.get_db_connection()
    conn.execute("DELETE FROM users WHERE email = ?", ("jane_unique99@test.com",))
    conn.commit()
    conn.close()

def test_signup_duplicate_email(logged_in):
    client = logged_in
    res = client.post("/signup", data={
        "full_name": "Someone Else",
        "email": "student@test.com",
        "password": "pass123"
    }, follow_redirects=True)
    assert b"already exists" in res.data

def test_signup_empty_fields(client):
    res = client.post("/signup", data={
        "full_name": "", "email": "", "password": ""
    }, follow_redirects=True)
    assert b"fill in" in res.data

def test_login_correct_details(logged_in):
    client = logged_in
    res = client.post("/login", data={
        "email": "student@test.com",
        "password": "password123"
    }, follow_redirects=True)
    assert res.status_code == 200

def test_login_wrong_password(logged_in):
    client = logged_in
    res = client.post("/login", data={
        "email": "student@test.com",
        "password": "wrongone"
    }, follow_redirects=True)
    assert b"Invalid" in res.data

def test_login_nonexistent_account(client):
    res = client.post("/login", data={
        "email": "nobody123@test.com",
        "password": "anything"
    }, follow_redirects=True)
    assert b"Invalid" in res.data

def test_login_empty_fields(client):
    res = client.post("/login", data={
        "email": "", "password": ""
    }, follow_redirects=True)
    assert b"email and password" in res.data

def test_logout_redirects(logged_in):
    res = logged_in.get("/logout", follow_redirects=True)
    assert res.status_code == 200

def test_forgot_password_success(logged_in):
    client = logged_in
    res = client.post("/forgot-password", data={
        "email": "student@test.com",
        "new_password": "newpass999",
        "confirm_password": "newpass999"
    }, follow_redirects=True)
    assert b"updated" in res.data

def test_forgot_password_mismatch(logged_in):
    client = logged_in
    res = client.post("/forgot-password", data={
        "email": "student@test.com",
        "new_password": "newpass999",
        "confirm_password": "notthesame"
    }, follow_redirects=True)
    assert b"do not match" in res.data

def test_forgot_password_unknown_email(client):
    res = client.post("/forgot-password", data={
        "email": "randomguy@test.com",
        "new_password": "pass123",
        "confirm_password": "pass123"
    }, follow_redirects=True)
    assert b"No account" in res.data