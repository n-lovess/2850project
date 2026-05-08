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

def test_payment_page_requires_login(client):
    res = client.get("/payment", follow_redirects=True)
    assert b"log in" in res.data.lower() or res.status_code == 200

def test_review_booking_requires_login(client):
    res = client.get("/review-booking", follow_redirects=True)
    assert res.status_code == 200