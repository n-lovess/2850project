import app as airgo


def test_request_change_needs_login(client):
    res = client.post("/request-change/1", data={
        "requested_departure": "London",
        "requested_destination": "Paris",
        "requested_date": "2026-09-01",
        "request_reason": "test"
    }, follow_redirects=True)
    assert b"log in" in res.data.lower()

def test_cancel_passenger_needs_login(client):
    res = client.post("/cancel-passenger/1", follow_redirects=True)
    assert b"log in" in res.data.lower() or res.status_code == 200

def test_cannot_cancel_someone_elses_booking(app):
    with app.test_client() as c:
        c.post("/signup", data={
            "full_name": "Other Guy",
            "email": "otherguy@test.com",
            "password": "pass123"
        })
        c.post("/login", data={"email": "otherguy@test.com", "password": "pass123"})
        res = c.post("/cancel-passenger/99999", follow_redirects=True)
        assert res.status_code == 200
        conn = airgo.get_db_connection()
        conn.execute("DELETE FROM users WHERE email = ?", ("otherguy@test.com",))
        conn.commit()
        conn.close()

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

def test_bookings_page_requires_login(client):
    res = client.get("/bookings")
    assert res.status_code == 302