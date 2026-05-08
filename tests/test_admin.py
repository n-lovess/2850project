
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



def test_admin_dashboard_loads_for_admin(app):
    with app.test_client() as c:
        c.post("/login", data={"email": "admin@airgo.com", "password": "admin123"})
        res = c.get("/admin")
        assert res.status_code == 200
        assert b"Admin Dashboard" in res.data

def test_admin_blocked_for_normal_user(logged_in):
    res = logged_in.get("/admin", follow_redirects=True)
    assert b"Admin access only" in res.data

def test_admin_blocked_for_guest(client):
    res = client.get("/admin", follow_redirects=True)
    assert b"Admin access only" in res.data

def test_admin_update_flight_status(app):
    with app.test_client() as c:
        c.post("/login", data={"email": "admin@airgo.com", "password": "admin123"})
        uid = get_user_id("admin@airgo.com")
        make_booking(uid, reference="ADM00001", seat="9A")
        bid = get_booking_id("ADM00001")
        res = c.post(f"/admin/update-flight-status/{bid}",
                     data={"flight_status": "Delayed"}, follow_redirects=True)
        assert b"updated" in res.data

def test_admin_invalid_flight_status_rejected(app):
    with app.test_client() as c:
        c.post("/login", data={"email": "admin@airgo.com", "password": "admin123"})
        uid = get_user_id("admin@airgo.com")
        make_booking(uid, reference="ADM00002", seat="9B")
        bid = get_booking_id("ADM00002")
        res = c.post(f"/admin/update-flight-status/{bid}",
                     data={"flight_status": "FAKEVALUE"}, follow_redirects=True)
        assert b"Invalid" in res.data

def test_admin_approve_change_request(app):
    with app.test_client() as c:
        c.post("/login", data={"email": "admin@airgo.com", "password": "admin123"})
        uid = get_user_id("admin@airgo.com")
        make_booking(uid, reference="ADM00003", seat="9C")
        bid = get_booking_id("ADM00003")
        res = c.post(f"/admin/update-change-status/{bid}",
                     data={"change_status": "Rejected"}, follow_redirects=True)
        assert b"updated" in res.data