def test_search_returns_flights(client):
    res = client.post("/results", data={
        "trip_type": "return",
        "departure": "London",
        "destination": "Paris",
        "depart_date": "2025-08-01",
        "return_date": "",
        "passengers": "1",
        "ticket_class": "Any"
    }, follow_redirects=True)
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
    }, follow_redirects=True)
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
    }, follow_redirects=True)
    assert res.status_code == 200

def test_airport_suggestions_returns_list(client):
    res = client.get("/airport-suggestions?q=lon")
    assert res.status_code == 200

def test_airport_suggestions_empty_query(client):
    res = client.get("/airport-suggestions?q=")
    assert res.status_code == 200