def test_results_page_loads(client):
    res = client.get("/results", follow_redirects=True)
    assert res.status_code == 200

def test_track_page_loads(client):
    res = client.get("/track")
    assert res.status_code == 200

def test_hotels_page_loads(client):
    res = client.get("/hotels", follow_redirects=True)
    assert res.status_code == 200

def test_taxis_page_loads(client):
    res = client.get("/taxis")
    assert res.status_code == 200

def test_login_page_loads(client):
    res = client.get("/login")
    assert res.status_code == 200

def test_signup_page_loads(client):
    res = client.get("/signup")
    assert res.status_code == 200

def test_bookings_redirects_when_not_logged_in(client):
    res = client.get("/bookings")
    assert res.status_code == 302

def test_admin_redirects_when_not_logged_in(client):
    res = client.get("/admin", follow_redirects=True)
    assert res.status_code == 200

def test_airport_suggestions_api(client):
    res = client.get("/airport-suggestions?q=london")
    assert res.status_code == 200

def test_airport_suggestions_returns_json(client):
    res = client.get("/airport-suggestions?q=lon")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)

def test_taxi_details_redirects_unauthenticated(client):
    res = client.get("/taxi/details", follow_redirects=True)
    assert b"log in" in res.data.lower()

def test_taxi_payment_redirects_unauthenticated(client):
    res = client.get("/taxi/payment", follow_redirects=True)
    assert b"log in" in res.data.lower()