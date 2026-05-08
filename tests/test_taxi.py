import app as airgo


def test_taxis_page_loads(client):
    res = client.get("/taxis")
    assert res.status_code == 200

def test_taxis_page_has_form(client):
    res = client.get("/taxis")
    assert b"Search Transfers" in res.data

def test_track_flight_page_loads(client):
    res = client.get("/track")
    assert res.status_code == 200

def test_track_flight_invalid_reference(client):
    res = client.post("/track", data={"booking_reference": "NOTREAL1"}, follow_redirects=True)
    assert res.status_code == 200

def test_track_flight_empty_reference(client):
    res = client.post("/track", data={"booking_reference": ""}, follow_redirects=True)
    assert res.status_code == 200

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
            "options": [{"name": "Standard Taxi", "desc": "Comfortable sedan", "price": 50.0, "icon": "🚕"}]
        }
        sess["taxi_pickup"] = "Leeds Bradford Airport (LBA)"
        sess["taxi_dropoff"] = "Belgrave Street, Leeds"
        sess["taxi_class"] = "Standard Taxi"
    res = logged_in.get("/taxi/details")
    assert res.status_code == 200

def test_taxi_details_missing_fields_shows_error(logged_in):
    with logged_in.session_transaction() as sess:
        sess["taxi_results"] = {
            "distance": 30.0, "duration": "45 mins",
            "options": [{"name": "Standard Taxi", "desc": "Comfortable sedan", "price": 50.0, "icon": "🚕"}]
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
            "distance": 30.0, "duration": "45 mins",
            "options": [{"name": "Standard Taxi", "desc": "Comfortable sedan", "price": 50.0, "icon": "🚕"}]
        }
        sess["taxi_pickup"] = "Leeds Bradford Airport"
        sess["taxi_dropoff"] = "Belgrave Street, Leeds"
        sess["taxi_class"] = "Standard Taxi"
    res = logged_in.post("/taxi/details", data={
        "first_name": "John", "last_name": "Smith",
        "phone": "07700900000", "alt_phone": "", "email": "john@test.com"
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
            "distance": 30.0, "duration": "45 mins",
            "options": [{"name": "Standard Taxi", "desc": "Comfortable sedan", "price": 50.0, "icon": "🚕"}]
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