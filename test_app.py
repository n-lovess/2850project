import pytest
import sqlite3
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# temp db so we dont touch the real one
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
    # delete test user after each test
    conn = airgo.get_db_connection()
    # Delete bookings first due to foreign key constraint
    conn.execute("DELETE FROM bookings WHERE email = ?", ("student@test.com",))
    conn.execute("DELETE FROM users WHERE email = ?", ("student@test.com",))
    conn.commit()
    conn.close()


# just gets the user id from the db
def get_user_id(email):
    conn = airgo.get_db_connection()
    row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return row["id"] if row else None


# inserts a fake booking so we can test things like cancel, update etc
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


# --- page loading ---

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


# --- signup ---

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


# --- login ---

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


# --- forgot password ---

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


# --- search ---

def test_search_returns_flights(client):
    res = client.post("/results", data={
        "trip_type": "return",
        "departure": "London",
        "destination": "Paris",
        "depart_date": "2025-08-01",
        "return_date": "",
        "passengers": "1",
        "ticket_class": "Any"
    })
    assert res.status_code == 200

def test_search_no_match_falls_back_to_sample(client):
    res = client.post("/results", data={
        "trip_type": "one-way",
        "departure": "XYZNOTREAL",
        "destination": "ABCNOTREAL",
        "depart_date": "2025-08-01",
        "return_date": "",
        "passengers": "1",
        "ticket_class": "Any"
    })
    assert res.status_code == 200

def test_search_filters_by_economy_class(client):
    res = client.post("/results", data={
        "trip_type": "one-way",
        "departure": "London",
        "destination": "New York",
        "depart_date": "2025-08-01",
        "return_date": "",
        "passengers": "1",
        "ticket_class": "Economy"
    })
    assert res.status_code == 200

def test_airport_suggestions_returns_list(client):
    res = client.get("/airport-suggestions?q=lon")
    assert res.status_code == 200

def test_airport_suggestions_empty_query(client):
    res = client.get("/airport-suggestions?q=")
    assert res.status_code == 200


# --- booking flow ---

def test_passenger_details_page_loads(logged_in):
    res = logged_in.get("/passenger-details/1")
    assert res.status_code == 200

def test_passenger_details_bad_flight_id(logged_in):
    res = logged_in.get("/passenger-details/9999", follow_redirects=True)
    assert res.status_code == 200

def test_seat_selection_without_session_data(logged_in):
    res = logged_in.get("/seat-selection", follow_redirects=True)
    assert res.status_code == 200

def test_seat_selection_rejects_blocked_seat(logged_in):
    with logged_in.session_transaction() as sess:
        sess["selected_flight"] = {
            "id": 1, "airline": "AirGo", "departure_city": "London",
            "destination_city": "Paris", "departure_time": "08:00",
            "arrival_time": "10:15", "flight_date": "2025-08-01",
            "ticket_class": "Economy", "price": 120
        }
    res = logged_in.post("/seat-selection", data={"seat": "1A"}, follow_redirects=True)
    assert res.status_code == 200

def test_seat_selection_rejects_no_seat(logged_in):
    res = logged_in.post("/seat-selection", data={"seat": ""}, follow_redirects=True)
    assert res.status_code == 200

def test_payment_redirects_if_not_logged_in(client):
    # set up session data but dont log in, should redirect to login
    with client.session_transaction() as sess:
        sess["selected_flight"] = {
            "id": 1, "airline": "AirGo", "departure_city": "London",
            "destination_city": "Paris", "departure_time": "08:00",
            "arrival_time": "10:15", "flight_date": "2025-08-01",
            "ticket_class": "Economy", "price": 120
        }
        sess["passenger_data"] = {
            "first_name": "Test", "last_name": "User",
            "email": "t@t.com", "phone": "000",
            "passport_number": "X", "meal_choice": "Standard Meal"
        }
        sess["selected_seat"] = "5A"
    res = client.get("/payment", follow_redirects=True)
    assert b"log in" in res.data.lower()


# --- manage bookings ---

def test_bookings_page_needs_login(client):
    res = client.get("/bookings")
    assert res.status_code == 302

def test_bookings_page_loads_when_logged_in(logged_in):
    res = logged_in.get("/bookings")
    assert res.status_code == 200
    assert b"Manage Booking" in res.data

def test_cancel_booking(logged_in):
    uid = get_user_id("student@test.com")
    make_booking(uid, reference="CAN00001", seat="7B")
    bid = get_booking_id("CAN00001")
    res = logged_in.post(f"/cancel-booking/{bid}", follow_redirects=True)
    assert b"cancelled" in res.data
    # double check its actually gone
    conn = airgo.get_db_connection()
    row = conn.execute("SELECT id FROM bookings WHERE id = ?", (bid,)).fetchone()
    conn.close()
    assert row is None

def test_update_meal(logged_in):
    uid = get_user_id("student@test.com")
    make_booking(uid, reference="MEAL0001", seat="7C")
    bid = get_booking_id("MEAL0001")
    res = logged_in.post(f"/update-meal/{bid}", data={"meal_choice": "Vegan Meal"}, follow_redirects=True)
    assert b"updated" in res.data

def test_request_change_submission(logged_in):
    uid = get_user_id("student@test.com")
    make_booking(uid, reference="CHG00001", seat="7D")
    bid = get_booking_id("CHG00001")
    res = logged_in.post(f"/request-change/{bid}", data={
        "requested_route": "London to Dubai",
        "requested_date": "2025-09-01",
        "request_reason": "changed plans"
    }, follow_redirects=True)
    assert b"submitted" in res.data

def test_request_change_all_empty(logged_in):
    uid = get_user_id("student@test.com")
    make_booking(uid, reference="CHG00002", seat="7E")
    bid = get_booking_id("CHG00002")
    res = logged_in.post(f"/request-change/{bid}", data={
        "requested_route": "", "requested_date": "", "request_reason": ""
    }, follow_redirects=True)
    assert b"at least one" in res.data

def test_boarding_pass_loads(logged_in):
    uid = get_user_id("student@test.com")
    make_booking(uid, reference="BRD00001", seat="7F")
    bid = get_booking_id("BRD00001")
    res = logged_in.get(f"/boarding-pass/{bid}")
    assert res.status_code == 200
    assert b"Boarding Pass" in res.data

def test_boarding_pass_wrong_user(logged_in):
    res = logged_in.get("/boarding-pass/99999", follow_redirects=True)
    assert b"not found" in res.data


# --- admin ---

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

# admin tests need their own client otherwise the session gets mixed up with logged_in
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
                     data={"change_status": "Approved"}, follow_redirects=True)
        assert b"updated" in res.data


# --- helper function tests ---

def test_calculate_points_basic():
    assert airgo.calculate_points(120) == 600

def test_calculate_points_zero():
    assert airgo.calculate_points(0) == 0

def test_booking_reference_is_8_chars():
    ref = airgo.generate_booking_reference()
    assert len(ref) == 8

def test_booking_reference_is_alphanumeric():
    ref = airgo.generate_booking_reference()
    assert ref.isalnum()

def test_find_flight_by_id_exists():
    f = airgo.find_flight_by_id(1)
    assert f is not None
    assert f["id"] == 1

def test_find_flight_by_id_not_found():
    f = airgo.find_flight_by_id(9999)
    assert f is None

def test_extras_total_all_zero():
    assert airgo.calculate_extras_total(0, 0, 0, 0) == 0

def test_extras_total_one_bag():
    assert airgo.calculate_extras_total(1, 0, 0, 0) == airgo.EXTRA_PRICES["extra_baggage"]

def test_tier_blue():
    info = airgo.get_tier_info(0)
    assert info["current_tier"] == "Blue"

def test_tier_silver():
    info = airgo.get_tier_info(1000)
    assert info["current_tier"] == "Silver"

def test_tier_gold():
    info = airgo.get_tier_info(3000)
    assert info["current_tier"] == "Gold"

def test_tier_platinum_no_next():
    info = airgo.get_tier_info(6000)
    assert info["current_tier"] == "Platinum"
    assert info["next_tier"] is None

def test_airport_match_by_city():
    result = airgo.matches_airport_search("london", "London", "LHR", "London All Airports", "London Heathrow")
    assert result is True

def test_airport_match_by_code():
    result = airgo.matches_airport_search("LHR", "London", "LHR", "London All Airports", "London Heathrow")
    assert result is True

def test_airport_no_match():
    result = airgo.matches_airport_search("Tokyo", "London", "LHR", "London All Airports", "London Heathrow")
    assert result is False

def test_upgrades_from_economy():
    upgrades = airgo.get_available_upgrades("Economy")
    assert "Business" in upgrades
    assert "First" in upgrades

def test_no_upgrades_from_first():
    upgrades = airgo.get_available_upgrades("First")
    assert upgrades == {}


# --- security ---

def test_cancel_booking_needs_login(client):
    res = client.post("/cancel-booking/1", follow_redirects=True)
    assert b"log in" in res.data.lower()

def test_update_meal_needs_login(client):
    res = client.post("/update-meal/1", data={"meal_choice": "Vegan Meal"}, follow_redirects=True)
    assert b"log in" in res.data.lower()

def test_update_extras_needs_login(client):
    res = client.post("/update-extras/1", data={"extra_baggage": "1"}, follow_redirects=True)
    assert b"log in" in res.data.lower()

def test_request_change_needs_login(client):
    res = client.post("/request-change/1", data={
        "requested_route": "London to Paris",
        "requested_date": "2025-09-01",
        "request_reason": "test"
    }, follow_redirects=True)
    assert b"log in" in res.data.lower()

def test_upgrade_booking_needs_login(client):
    res = client.post("/upgrade-booking/1", data={"new_class": "Business"}, follow_redirects=True)
    assert b"log in" in res.data.lower()

def test_cannot_cancel_someone_elses_booking(app):
    # made a separate user for this one, kept failing when using logged_in fixture
    with app.test_client() as c:
        c.post("/signup", data={
            "full_name": "Other Guy",
            "email": "otherguy@test.com",
            "password": "pass123"
        })
        c.post("/login", data={"email": "otherguy@test.com", "password": "pass123"})
        uid = get_user_id("otherguy@test.com")
        before = get_booking_count(uid)
        c.post("/cancel-booking/99999", follow_redirects=True)
        after = get_booking_count(uid)
        assert before == after
        conn = airgo.get_db_connection()
        conn.execute("DELETE FROM bookings WHERE user_id = ?", (uid,))
        conn.execute("DELETE FROM users WHERE email = ?", ("otherguy@test.com",))
        conn.commit()
        conn.close()


# ==============
# API Tests
# ==============

def test_api_get_flights(client):
    res = client.get("/api/flights")
    assert res.status_code == 200
    data = res.get_json()
    assert data["error"] is None
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 6
    assert data["data"][0]["id"] == 1


def test_api_get_flight_by_id(client):
    res = client.get("/api/flights/1")
    assert res.status_code == 200
    data = res.get_json()
    assert data["error"] is None
    assert data["data"]["id"] == 1
    assert data["data"]["from_code"] == "LHR"


def test_api_get_flight_not_found(client):
    res = client.get("/api/flights/99999")
    assert res.status_code == 404
    data = res.get_json()
    assert data["error"] is not None
    assert data["data"] is None


def test_api_bookings_unauthenticated(client):
    res = client.get("/api/bookings")
    assert res.status_code == 401
    data = res.get_json()
    assert "Unauthorized" in data["error"]


def test_api_bookings_authenticated(logged_in):
    res = logged_in.get("/api/bookings")
    assert res.status_code == 200
    data = res.get_json()
    assert data["error"] is None
    assert isinstance(data["data"], list)


def test_api_single_booking_not_found(logged_in):
    res = logged_in.get("/api/bookings/99999")
    assert res.status_code == 404
    data = res.get_json()
    assert data["error"] is not None


def test_api_delete_booking_unauthenticated(client):
    res = client.delete("/api/bookings/1")
    assert res.status_code == 401


def test_api_delete_booking_not_found(logged_in):
    res = logged_in.delete("/api/bookings/99999")
    assert res.status_code == 404


def test_api_admin_reports_denied_normal_user(logged_in):
    res = logged_in.get("/api/admin/reports/bookings-per-flight")
    assert res.status_code == 403


def test_api_admin_reports_access_admin(app):
    with app.test_client() as c:
        c.post("/login", data={"email": "admin@airgo.com", "password": "admin123"})
        res = c.get("/api/admin/reports/bookings-per-flight")
        assert res.status_code == 200
        data = res.get_json()
        assert data["error"] is None
        assert isinstance(data["data"], list)


def test_api_admin_reports_popular_routes_denied_normal_user(logged_in):
    res = logged_in.get("/api/admin/reports/popular-routes")
    assert res.status_code == 403
    data = res.get_json()
    assert "Forbidden: Admin access only" in data["error"]


def test_api_admin_reports_peak_times_denied_normal_user(logged_in):
    res = logged_in.get("/api/admin/reports/peak-booking-times")
    assert res.status_code == 403
    data = res.get_json()
    assert "Forbidden: Admin access only" in data["error"]


# ==============
# Flight Tracker Tests
# ==============

def test_track_flight_page_loads(client):
    res = client.get("/track")
    assert res.status_code == 200

def test_track_flight_valid_reference(logged_in):
    uid = get_user_id("student@test.com")
    make_booking(uid, reference="TRK00001", seat="5A")
    res = logged_in.post("/track", data={"booking_reference": "TRK00001"}, follow_redirects=True)
    assert res.status_code == 200

def test_track_flight_invalid_reference(client):
    res = client.post("/track", data={"booking_reference": "NOTREAL1"}, follow_redirects=True)
    assert res.status_code == 200

def test_track_flight_empty_reference(client):
    res = client.post("/track", data={"booking_reference": ""}, follow_redirects=True)
    assert res.status_code == 200

def test_track_flight_lowercase_reference(logged_in):
    uid = get_user_id("student@test.com")
    make_booking(uid, reference="TRK00002", seat="5B")
    res = logged_in.post("/track", data={"booking_reference": "trk00002"}, follow_redirects=True)
    assert res.status_code == 200


# ==============
# Taxi Flow Tests
# ==============

def test_taxis_page_loads(client):
    res = client.get("/taxis")
    assert res.status_code == 200

def test_taxis_page_has_form(client):
    res = client.get("/taxis")
    assert b"Search Transfers" in res.data

def test_taxi_details_redirects_if_not_logged_in(client):
    res = client.get("/taxi/details", follow_redirects=True)
    assert b"log in" in res.data.lower()

def test_taxi_details_redirects_if_no_session_data(logged_in):
    res = logged_in.get("/taxi/details", follow_redirects=True)
    assert res.status_code == 200

def test_taxi_details_loads_with_session(logged_in):
    with logged_in.session_transaction() as sess:
        sess["taxi_results"] = {
            "distance": 30.0,
            "duration": "45 mins",
            "options": [{
                "name": "Standard Taxi",
                "desc": "Comfortable sedan",
                "price": 50.0,
                "icon": "🚕"
            }]
        }
        sess["taxi_pickup"] = "Leeds Bradford Airport (LBA)"
        sess["taxi_dropoff"] = "Belgrave Street, Leeds"
        sess["taxi_class"] = "Standard Taxi"
    res = logged_in.get("/taxi/details")
    assert res.status_code == 200

def test_taxi_details_missing_fields_shows_error(logged_in):
    with logged_in.session_transaction() as sess:
        sess["taxi_results"] = {
            "distance": 30.0,
            "duration": "45 mins",
            "options": [{
                "name": "Standard Taxi",
                "desc": "Comfortable sedan",
                "price": 50.0,
                "icon": "🚕"
            }]
        }
        sess["taxi_pickup"] = "Leeds Bradford Airport"
        sess["taxi_dropoff"] = "Belgrave Street, Leeds"
        sess["taxi_class"] = "Standard Taxi"
    res = logged_in.post("/taxi/details", data={
        "first_name": "", "last_name": "", "phone": "", "email": ""
    }, follow_redirects=True)
    assert b"required" in res.data.lower()

def test_taxi_details_valid_submission_redirects(logged_in):
    with logged_in.session_transaction() as sess:
        sess["taxi_results"] = {
            "distance": 30.0,
            "duration": "45 mins",
            "options": [{
                "name": "Standard Taxi",
                "desc": "Comfortable sedan",
                "price": 50.0,
                "icon": "🚕"
            }]
        }
        sess["taxi_pickup"] = "Leeds Bradford Airport"
        sess["taxi_dropoff"] = "Belgrave Street, Leeds"
        sess["taxi_class"] = "Standard Taxi"
    res = logged_in.post("/taxi/details", data={
        "first_name": "John",
        "last_name": "Smith",
        "phone": "07700900000",
        "alt_phone": "",
        "email": "john@test.com"
    }, follow_redirects=False)
    assert res.status_code == 302

def test_taxi_payment_redirects_if_not_logged_in(client):
    res = client.get("/taxi/payment", follow_redirects=True)
    assert b"log in" in res.data.lower()

def test_taxi_payment_redirects_if_no_session(logged_in):
    res = logged_in.get("/taxi/payment", follow_redirects=True)
    assert res.status_code == 200

def test_taxi_payment_loads_with_full_session(logged_in):
    with logged_in.session_transaction() as sess:
        sess["taxi_results"] = {
            "distance": 30.0,
            "duration": "45 mins",
            "options": [{
                "name": "Standard Taxi",
                "desc": "Comfortable sedan",
                "price": 50.0,
                "icon": "🚕"
            }]
        }
        sess["taxi_pickup"] = "Leeds Bradford Airport"
        sess["taxi_dropoff"] = "Belgrave Street, Leeds"
        sess["taxi_class"] = "Standard Taxi"
        sess["taxi_passenger"] = {
            "first_name": "John", "last_name": "Smith",
            "phone": "07700900000", "alt_phone": "", "email": "john@test.com"
        }
    res = logged_in.get("/taxi/payment")
    assert res.status_code == 200

def test_taxi_payment_rejects_missing_card_fields(logged_in):
    with logged_in.session_transaction() as sess:
        sess["taxi_results"] = {
            "distance": 30.0, "duration": "45 mins",
            "options": [{"name": "Standard Taxi", "desc": "Sedan", "price": 50.0, "icon": "🚕"}]
        }
        sess["taxi_pickup"] = "Leeds Airport"
        sess["taxi_dropoff"] = "Leeds City"
        sess["taxi_class"] = "Standard Taxi"
        sess["taxi_passenger"] = {
            "first_name": "John", "last_name": "Smith",
            "phone": "07700900000", "alt_phone": "", "email": "john@test.com"
        }
    res = logged_in.post("/taxi/payment", data={
        "card_name": "", "card_number": "", "expiry_date": "", "cvv": "",
        "accept_terms": "on", "points_to_use": "0"
    }, follow_redirects=True)
    assert b"fill in all payment" in res.data.lower()

def test_taxi_payment_rejects_no_terms(logged_in):
    with logged_in.session_transaction() as sess:
        sess["taxi_results"] = {
            "distance": 30.0, "duration": "45 mins",
            "options": [{"name": "Standard Taxi", "desc": "Sedan", "price": 50.0, "icon": "🚕"}]
        }
        sess["taxi_pickup"] = "Leeds Airport"
        sess["taxi_dropoff"] = "Leeds City"
        sess["taxi_class"] = "Standard Taxi"
        sess["taxi_passenger"] = {
            "first_name": "John", "last_name": "Smith",
            "phone": "07700900000", "alt_phone": "", "email": "john@test.com"
        }
    res = logged_in.post("/taxi/payment", data={
        "card_name": "John Smith", "card_number": "1234567890123456",
        "expiry_date": "2026-01", "cvv": "123", "points_to_use": "0"
    }, follow_redirects=True)
    assert b"terms" in res.data.lower()

def test_taxi_payment_rejects_invalid_card_number(logged_in):
    with logged_in.session_transaction() as sess:
        sess["taxi_results"] = {
            "distance": 30.0, "duration": "45 mins",
            "options": [{"name": "Standard Taxi", "desc": "Sedan", "price": 50.0, "icon": "🚕"}]
        }
        sess["taxi_pickup"] = "Leeds Airport"
        sess["taxi_dropoff"] = "Leeds City"
        sess["taxi_class"] = "Standard Taxi"
        sess["taxi_passenger"] = {
            "first_name": "John", "last_name": "Smith",
            "phone": "07700900000", "alt_phone": "", "email": "john@test.com"
        }
    res = logged_in.post("/taxi/payment", data={
        "card_name": "John Smith", "card_number": "123",
        "expiry_date": "2026-01", "cvv": "123",
        "accept_terms": "on", "points_to_use": "0"
    }, follow_redirects=True)
    assert b"16 digits" in res.data.lower()

def test_taxi_payment_rejects_invalid_cvv(logged_in):
    with logged_in.session_transaction() as sess:
        sess["taxi_results"] = {
            "distance": 30.0, "duration": "45 mins",
            "options": [{"name": "Standard Taxi", "desc": "Sedan", "price": 50.0, "icon": "🚕"}]
        }
        sess["taxi_pickup"] = "Leeds Airport"
        sess["taxi_dropoff"] = "Leeds City"
        sess["taxi_class"] = "Standard Taxi"
        sess["taxi_passenger"] = {
            "first_name": "John", "last_name": "Smith",
            "phone": "07700900000", "alt_phone": "", "email": "john@test.com"
        }
    res = logged_in.post("/taxi/payment", data={
        "card_name": "John Smith", "card_number": "1234567890123456",
        "expiry_date": "2026-01", "cvv": "99",
        "accept_terms": "on", "points_to_use": "0"
    }, follow_redirects=True)
    assert b"cvv" in res.data.lower()

def test_taxi_confirmation_redirects_if_no_reference(logged_in):
    res = logged_in.get("/taxi/confirmation", follow_redirects=True)
    assert res.status_code == 200

def test_full_taxi_booking_flow(app):
    with app.test_client() as c:
        c.post("/signup", data={
            "full_name": "Taxi Tester",
            "email": "taxitester@test.com",
            "password": "pass123"
        })
        c.post("/login", data={"email": "taxitester@test.com", "password": "pass123"})

        with c.session_transaction() as sess:
            sess["taxi_results"] = {
                "distance": 30.0, "duration": "45 mins",
                "options": [{"name": "Standard Taxi", "desc": "Sedan", "price": 50.0, "icon": "🚕"}]
            }
            sess["taxi_pickup"] = "Leeds Bradford Airport"
            sess["taxi_dropoff"] = "Belgrave Street, Leeds"
            sess["taxi_class"] = "Standard Taxi"

        c.post("/taxi/details", data={
            "first_name": "Taxi", "last_name": "Tester",
            "phone": "07700900000", "alt_phone": "", "email": "taxitester@test.com"
        })

        res = c.post("/taxi/payment", data={
            "card_name": "Taxi Tester",
            "card_number": "1234567890123456",
            "expiry_date": "2026-01",
            "cvv": "123",
            "accept_terms": "on",
            "points_to_use": "0"
        }, follow_redirects=True)

        assert res.status_code == 200

        conn = airgo.get_db_connection()
        uid = conn.execute("SELECT id FROM users WHERE email = ?", ("taxitester@test.com",)).fetchone()
        if uid:
            conn.execute("DELETE FROM taxi_bookings WHERE user_id = ?", (uid["id"],))
            conn.execute("DELETE FROM users WHERE email = ?", ("taxitester@test.com",))
            conn.commit()
        conn.close()


# ==============
# Security Tests
# ==============

def test_sql_injection_login(client):
    res = client.post("/login", data={
        "email": "' OR '1'='1",
        "password": "' OR '1'='1"
    }, follow_redirects=True)
    assert b"Invalid" in res.data or b"email and password" in res.data

def test_sql_injection_signup(client):
    res = client.post("/signup", data={
        "full_name": "'; DROP TABLE users; --",
        "email": "inject@test.com",
        "password": "pass123"
    }, follow_redirects=True)
    conn = airgo.get_db_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    assert users is not None

def test_xss_in_signup_name(client):
    res = client.post("/signup", data={
        "full_name": "<script>alert('xss')</script>",
        "email": "xss_test_unique@test.com",
        "password": "pass123"
    }, follow_redirects=True)
    assert b"<script>alert" not in res.data
    conn = airgo.get_db_connection()
    conn.execute("DELETE FROM users WHERE email = ?", ("xss_test_unique@test.com",))
    conn.commit()
    conn.close()

def test_taxi_details_requires_login_post(client):
    res = client.post("/taxi/details", data={
        "first_name": "John", "last_name": "Smith",
        "phone": "07700900000", "email": "john@test.com"
    }, follow_redirects=True)
    assert b"log in" in res.data.lower()

def test_taxi_payment_requires_login_post(client):
    res = client.post("/taxi/payment", data={
        "card_name": "John Smith", "card_number": "1234567890123456",
        "expiry_date": "2026-01", "cvv": "123", "accept_terms": "on"
    }, follow_redirects=True)
    assert b"log in" in res.data.lower()

def test_direct_taxi_confirmation_without_booking(client):
    res = client.get("/taxi/confirmation", follow_redirects=True)
    assert res.status_code == 200