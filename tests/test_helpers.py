import app as airgo


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

def test_find_flight_by_id_exists(app):
    with app.test_request_context():
        f = airgo.find_flight_by_id(1)
        assert f is not None

def test_find_flight_by_id_not_found(app):
    with app.test_request_context():
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