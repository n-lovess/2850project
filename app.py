from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
import sqlite3
import os
import csv

app = Flask(__name__)
app.secret_key = "super_secret_key_change_this_later"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "bookings.db")


def load_airports():
    airports = []
    seen_codes = set()
    seen_city_all = set()

    file_path = os.path.join(BASE_DIR, "data", "airports.csv")

    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            iata = (row.get("iata_code") or "").strip()
            airport_type = (row.get("type") or "").strip()
            city = (row.get("municipality") or row.get("name") or "").strip()
            airport_name = (row.get("name") or "").strip()

            if not iata:
                continue

            if airport_type not in ["large_airport", "medium_airport"]:
                continue

            if iata in seen_codes:
                continue

            seen_codes.add(iata)

            airports.append({
                "city": city,
                "name": airport_name,
                "code": iata
            })

            city_key = city.lower()
            if city and city_key not in seen_city_all:
                seen_city_all.add(city_key)
                city_code = city[:3].upper() if len(city) >= 3 else city.upper()

                airports.append({
                    "city": city,
                    "name": f"{city} All Airports",
                    "code": city_code
                })

    return airports


AIRPORTS = load_airports()

SAMPLE_FLIGHTS = [
    {
        "id": 1,
        "airline": "AirGo",
        "from": "London Heathrow",
        "from_city": "London",
        "from_code": "LHR",
        "airport_group": "London All Airports",
        "to": "Paris Charles de Gaulle",
        "to_city": "Paris",
        "to_code": "CDG",
        "destination_group": "Paris All Airports",
        "departure_time": "08:00",
        "arrival_time": "10:15",
        "price": 120,
        "class": "Economy",
        "seats_left": 14
    },
    {
        "id": 2,
        "airline": "AirGo",
        "from": "London Gatwick",
        "from_city": "London",
        "from_code": "LGW",
        "airport_group": "London All Airports",
        "to": "Paris Orly",
        "to_city": "Paris",
        "to_code": "ORY",
        "destination_group": "Paris All Airports",
        "departure_time": "12:30",
        "arrival_time": "14:45",
        "price": 185,
        "class": "Premium Economy",
        "seats_left": 7
    },
    {
        "id": 3,
        "airline": "AirGo",
        "from": "London Stansted",
        "from_city": "London",
        "from_code": "STN",
        "airport_group": "London All Airports",
        "to": "Dubai International",
        "to_city": "Dubai",
        "to_code": "DXB",
        "destination_group": "Dubai All Airports",
        "departure_time": "18:20",
        "arrival_time": "03:35",
        "price": 310,
        "class": "Business",
        "seats_left": 3
    },
    {
        "id": 4,
        "airline": "AirGo",
        "from": "Paris Charles de Gaulle",
        "from_city": "Paris",
        "from_code": "CDG",
        "airport_group": "Paris All Airports",
        "to": "Dubai International",
        "to_city": "Dubai",
        "to_code": "DXB",
        "destination_group": "Dubai All Airports",
        "departure_time": "09:45",
        "arrival_time": "18:10",
        "price": 275,
        "class": "Economy",
        "seats_left": 11
    },
    {
        "id": 5,
        "airline": "AirGo",
        "from": "Dubai International",
        "from_city": "Dubai",
        "from_code": "DXB",
        "airport_group": "Dubai All Airports",
        "to": "London Heathrow",
        "to_city": "London",
        "to_code": "LHR",
        "destination_group": "London All Airports",
        "departure_time": "14:00",
        "arrival_time": "18:45",
        "price": 420,
        "class": "Business",
        "seats_left": 5
    },
    {
        "id": 6,
        "airline": "AirGo",
        "from": "London City",
        "from_city": "London",
        "from_code": "LCY",
        "airport_group": "London All Airports",
        "to": "John F. Kennedy",
        "to_city": "New York",
        "to_code": "JFK",
        "destination_group": "New York All Airports",
        "departure_time": "10:00",
        "arrival_time": "13:25",
        "price": 510,
        "class": "Premium Economy",
        "seats_left": 8
    }
]

CLASS_BENEFITS = {
    "Economy": {
        "baggage": "1 cabin bag",
        "meal": "Standard meal",
        "seat_selection": "Standard seat selection",
        "lounge": "Not included",
        "flexibility": "Low flexibility"
    },
    "Premium Economy": {
        "baggage": "1 cabin bag + 1 checked bag",
        "meal": "Premium meal",
        "seat_selection": "Included",
        "lounge": "Not included",
        "flexibility": "Medium flexibility"
    },
    "Business": {
        "baggage": "2 checked bags + 1 cabin bag",
        "meal": "Business class dining",
        "seat_selection": "Priority seat selection",
        "lounge": "Included",
        "flexibility": "High flexibility"
    },
    "First": {
        "baggage": "3 checked bags + 2 cabin bags",
        "meal": "First class dining",
        "seat_selection": "Luxury suite selection",
        "lounge": "Included",
        "flexibility": "Maximum flexibility"
    }
}

MEAL_OPTIONS = {
    "Economy": [
        "Standard Meal",
        "Vegetarian Meal",
        "Vegan Meal",
        "Halal Meal"
    ],
    "Premium Economy": [
        "Premium Standard Meal",
        "Vegetarian Meal",
        "Vegan Meal",
        "Halal Meal"
    ],
    "Business": [
        "Business Signature Meal",
        "Vegetarian Meal",
        "Vegan Meal",
        "Halal Meal",
        "Gluten Free Meal"
    ],
    "First": [
        "First Class Signature Dining",
        "Vegetarian Meal",
        "Vegan Meal",
        "Halal Meal",
        "Gluten Free Meal"
    ]
}

COMMON_MEAL_OPTIONS = [
    "Standard Meal",
    "Vegetarian Meal",
    "Vegan Meal",
    "Halal Meal",
    "Gluten Free Meal"
]

UPGRADE_PRICES = {
    "Economy": {
        "Premium Economy": 65,
        "Business": 190,
        "First": 380
    },
    "Premium Economy": {
        "Business": 125,
        "First": 315
    },
    "Business": {
        "First": 190
    },
    "First": {}
}

LOYALTY_TIERS = [
    {"name": "Blue", "min_points": 0},
    {"name": "Silver", "min_points": 1000},
    {"name": "Gold", "min_points": 3000},
    {"name": "Platinum", "min_points": 6000}
]

EXTRA_PRICES = {
    "extra_baggage": 35,
    "priority_boarding": 20,
    "wifi_package": 12,
    "lounge_access": 45
}

DEFAULT_FLIGHT_STATUS = "Scheduled"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            booking_reference TEXT NOT NULL UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            passport_number TEXT NOT NULL,
            airline TEXT NOT NULL,
            departure_airport TEXT NOT NULL,
            departure_city TEXT NOT NULL,
            departure_code TEXT NOT NULL,
            destination_airport TEXT NOT NULL,
            destination_city TEXT NOT NULL,
            destination_code TEXT NOT NULL,
            flight_date TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            arrival_time TEXT NOT NULL,
            ticket_class TEXT NOT NULL,
            meal_choice TEXT NOT NULL,
            seat TEXT NOT NULL,
            price REAL NOT NULL,
            points_earned INTEGER NOT NULL DEFAULT 0,
            trip_type TEXT NOT NULL DEFAULT 'return',
            change_request TEXT,
            change_status TEXT NOT NULL DEFAULT 'None',
            flight_status TEXT NOT NULL DEFAULT 'Scheduled',
            extra_baggage INTEGER NOT NULL DEFAULT 0,
            priority_boarding INTEGER NOT NULL DEFAULT 0,
            wifi_package INTEGER NOT NULL DEFAULT 0,
            lounge_access INTEGER NOT NULL DEFAULT 0,
            requested_route TEXT DEFAULT '',
            requested_date TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    admin_email = "admin@airgo.com"
    existing_admin = conn.execute(
        "SELECT id FROM users WHERE email = ?",
        (admin_email,)
    ).fetchone()

    if not existing_admin:
        conn.execute("""
            INSERT INTO users (full_name, email, password_hash)
            VALUES (?, ?, ?)
        """, (
            "AirGo Admin",
            admin_email,
            generate_password_hash("admin123")
        ))

    conn.commit()
    conn.close()


def generate_booking_reference(length=8):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def find_flight_by_id(flight_id):
    for flight in SAMPLE_FLIGHTS:
        if flight["id"] == flight_id:
            return flight
    return None


def calculate_points(price):
    return int(price * 5)


def matches_airport_search(user_input, city, airport_code, airport_group, airport_name):
    if not user_input:
        return True

    text = user_input.strip().lower()

    if (
        text in city.lower()
        or text in airport_code.lower()
        or text in airport_group.lower()
        or text in airport_name.lower()
    ):
        return True

    if "(" in text and ")" in text:
        start = text.find("(") + 1
        end = text.find(")")
        bracket_code = text[start:end].strip().lower()
        if bracket_code == airport_code.lower():
            return True

    return False


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user


def is_admin():
    return session.get("user_email") == "admin@airgo.com"


def get_booked_seats_for_flight(flight):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT seat FROM bookings
        WHERE airline = ?
          AND departure_airport = ?
          AND destination_airport = ?
          AND departure_time = ?
          AND arrival_time = ?
          AND flight_date = ?
    """, (
        flight["airline"],
        flight["from"],
        flight["to"],
        flight["departure_time"],
        flight["arrival_time"],
        session.get("search_data", {}).get("depart_date", "")
    )).fetchall()
    conn.close()

    return {row["seat"] for row in rows}


def generate_seat_map(flight):
    rows = 10
    cols = ["A", "B", "C", "D", "E", "F"]

    permanently_unavailable = {
        "1A", "1F", "2C", "3D", "4B", "5E", "7A", "8F"
    }

    booked_seats = get_booked_seats_for_flight(flight)
    all_unavailable = permanently_unavailable.union(booked_seats)

    seat_rows = []

    for row_number in range(1, rows + 1):
        current_row = []
        for col in cols:
            seat_code = f"{row_number}{col}"
            current_row.append({
                "seat": seat_code,
                "available": seat_code not in all_unavailable
            })
        seat_rows.append(current_row)

    return seat_rows


def calculate_extras_total(extra_baggage, priority_boarding, wifi_package, lounge_access):
    return (
        int(extra_baggage) * EXTRA_PRICES["extra_baggage"]
        + int(priority_boarding) * EXTRA_PRICES["priority_boarding"]
        + int(wifi_package) * EXTRA_PRICES["wifi_package"]
        + int(lounge_access) * EXTRA_PRICES["lounge_access"]
    )


def get_available_upgrades(current_class):
    return UPGRADE_PRICES.get(current_class, {})


def get_tier_info(total_points):
    current_tier = LOYALTY_TIERS[0]
    next_tier = None

    for idx, tier in enumerate(LOYALTY_TIERS):
        if total_points >= tier["min_points"]:
            current_tier = tier
            if idx + 1 < len(LOYALTY_TIERS):
                next_tier = LOYALTY_TIERS[idx + 1]
            else:
                next_tier = None

    if next_tier:
        current_min = current_tier["min_points"]
        next_min = next_tier["min_points"]
        progress_range = next_min - current_min
        progress_value = total_points - current_min
        progress_percent = int((progress_value / progress_range) * 100) if progress_range > 0 else 100
        points_to_next = max(0, next_min - total_points)
    else:
        progress_percent = 100
        points_to_next = 0

    return {
        "current_tier": current_tier["name"],
        "next_tier": next_tier["name"] if next_tier else None,
        "progress_percent": progress_percent,
        "points_to_next": points_to_next
    }


def enrich_booking_for_display(booking):
    booking_dict = dict(booking)
    booking_dict["extras_total"] = calculate_extras_total(
        booking_dict["extra_baggage"],
        booking_dict["priority_boarding"],
        booking_dict["wifi_package"],
        booking_dict["lounge_access"]
    )
    booking_dict["available_upgrades"] = get_available_upgrades(booking_dict["ticket_class"])
    return booking_dict


def find_airport_by_city(city_name):
    city_name = city_name.strip().lower()
    preferred_all = None
    first_match = None

    for airport in AIRPORTS:
        if airport["city"].lower() == city_name:
            if not first_match:
                first_match = airport
            if "all airports" in airport["name"].lower():
                preferred_all = airport

    return preferred_all or first_match


def apply_approved_change_to_booking(conn, booking):
    requested_route = (booking["requested_route"] or "").strip()
    requested_date = (booking["requested_date"] or "").strip()

    updated_departure_airport = booking["departure_airport"]
    updated_departure_city = booking["departure_city"]
    updated_departure_code = booking["departure_code"]
    updated_destination_airport = booking["destination_airport"]
    updated_destination_city = booking["destination_city"]
    updated_destination_code = booking["destination_code"]
    updated_flight_date = booking["flight_date"]

    if requested_route and " to " in requested_route.lower():
        parts = requested_route.split(" to ")
        if len(parts) == 2:
            dep_city_raw = parts[0].strip()
            dest_city_raw = parts[1].strip()

            dep_airport = find_airport_by_city(dep_city_raw)
            dest_airport = find_airport_by_city(dest_city_raw)

            if dep_airport:
                updated_departure_airport = dep_airport["name"]
                updated_departure_city = dep_airport["city"]
                updated_departure_code = dep_airport["code"]

            if dest_airport:
                updated_destination_airport = dest_airport["name"]
                updated_destination_city = dest_airport["city"]
                updated_destination_code = dest_airport["code"]

    if requested_date:
        updated_flight_date = requested_date

    conn.execute("""
        UPDATE bookings
        SET departure_airport = ?,
            departure_city = ?,
            departure_code = ?,
            destination_airport = ?,
            destination_city = ?,
            destination_code = ?,
            flight_date = ?
        WHERE id = ?
    """, (
        updated_departure_airport,
        updated_departure_city,
        updated_departure_code,
        updated_destination_airport,
        updated_destination_city,
        updated_destination_code,
        updated_flight_date,
        booking["id"]
    ))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not full_name or not email or not password:
            flash("Please fill in all sign up fields.", "error")
            return render_template("signup.html")

        conn = get_db_connection()
        existing_user = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_user:
            conn.close()
            flash("An account with that email already exists.", "error")
            return render_template("signup.html")

        password_hash = generate_password_hash(password)

        cursor = conn.execute("""
            INSERT INTO users (full_name, email, password_hash)
            VALUES (?, ?, ?)
        """, (full_name, email, password_hash))
        conn.commit()

        session["user_id"] = cursor.lastrowid
        session["user_name"] = full_name
        session["user_email"] = email

        conn.close()

        flash("Account created successfully.", "success")
        return redirect(session.pop("post_login_redirect", url_for("home")))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter your email and password.", "error")
            return render_template("login.html")

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        conn.close()

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        session["user_id"] = user["id"]
        session["user_name"] = user["full_name"]
        session["user_email"] = user["email"]

        flash("Logged in successfully.", "success")
        return redirect(session.pop("post_login_redirect", url_for("home")))

    return render_template("login.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not email or not new_password or not confirm_password:
            flash("Please fill in all fields.", "error")
            return render_template("forgot_password.html")

        if new_password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("forgot_password.html")

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if not user:
            conn.close()
            flash("No account was found with that email.", "error")
            return render_template("forgot_password.html")

        conn.execute("""
            UPDATE users
            SET password_hash = ?
            WHERE email = ?
        """, (generate_password_hash(new_password), email))
        conn.commit()
        conn.close()

        flash("Password updated successfully. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("forgot_password.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.route("/airport-suggestions")
def airport_suggestions():
    query = request.args.get("q", "").strip().lower()

    if not query:
        return jsonify([])

    matches = [
        airport for airport in AIRPORTS
        if query in airport["city"].lower()
        or query in airport["name"].lower()
        or query in airport["code"].lower()
    ]

    return jsonify(matches[:10])


@app.route("/results", methods=["POST"])
def results():
    trip_type = request.form.get("trip_type", "return")
    departure = request.form.get("departure", "").strip()
    destination = request.form.get("destination", "").strip()
    depart_date = request.form.get("depart_date", "")
    return_date = request.form.get("return_date", "")
    departure_2 = request.form.get("departure_2", "").strip()
    destination_2 = request.form.get("destination_2", "").strip()
    depart_date_2 = request.form.get("depart_date_2", "")
    passengers = request.form.get("passengers", "1")
    ticket_class = request.form.get("ticket_class", "Any")

    matching_flights = [
        flight for flight in SAMPLE_FLIGHTS
        if matches_airport_search(
            departure,
            flight["from_city"],
            flight["from_code"],
            flight["airport_group"],
            flight["from"]
        )
        and matches_airport_search(
            destination,
            flight["to_city"],
            flight["to_code"],
            flight["destination_group"],
            flight["to"]
        )
    ]

    if ticket_class != "Any":
        matching_flights = [
            flight for flight in matching_flights
            if flight["class"].lower() == ticket_class.lower()
        ]

    search_data = {
        "trip_type": trip_type,
        "departure": departure,
        "destination": destination,
        "depart_date": depart_date,
        "return_date": return_date,
        "departure_2": departure_2,
        "destination_2": destination_2,
        "depart_date_2": depart_date_2,
        "passengers": passengers,
        "ticket_class": ticket_class
    }

    session["search_data"] = search_data

    if not matching_flights:
        flash("No exact matches found. Showing sample flights instead.", "info")
        matching_flights = SAMPLE_FLIGHTS

    return render_template(
        "results.html",
        flights=matching_flights,
        search_data=search_data,
        class_benefits=CLASS_BENEFITS
    )


@app.route("/passenger-details/<int:flight_id>", methods=["GET", "POST"])
def passenger_details(flight_id):
    selected_flight = find_flight_by_id(flight_id)

    if not selected_flight:
        flash("Selected flight was not found.", "error")
        return redirect(url_for("home"))


    if request.method == "POST":
        assistance_required = request.form.get("assistance_required")
        assistance_options = request.form.getlist("assistance_options")
        other_assistance = request.form.get("other_assistance")

        passenger_data = {
            "first_name": request.form.get("first_name", "").strip(),
            "last_name": request.form.get("last_name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "passport_number": request.form.get("passport_number", "").strip(),
            "assistance_required": assistance_required,
            "assistance_options": assistance_options,
            "other_assistance": other_assistance
        }

        required_fields = [
            passenger_data["first_name"],
            passenger_data["last_name"],
            passenger_data["email"],
            passenger_data["phone"],
            passenger_data["passport_number"],
        ]

        if not all(required_fields):
            flash("Please fill in all passenger details.", "error")
            return render_template(
                "passenger_details.html",
                flight=selected_flight,
                benefits=CLASS_BENEFITS.get(selected_flight["class"], {}),
            )

        session["selected_flight"] = selected_flight
        session["passenger_data"] = passenger_data
        session.pop("selected_seat", None)

        if not session.get("user_id"):
            session["post_login_redirect"] = url_for("extras")
            flash("Please log in or sign up to continue your booking.", "error")
            return redirect(url_for("login"))

        return redirect(url_for("extras"))

    return render_template(
        "passenger_details.html",
        flight=selected_flight,
        benefits=CLASS_BENEFITS.get(selected_flight["class"], {}),
    )

@app.route("/seat-selection", methods=["GET", "POST"])
def seat_selection():
    selected_flight = session.get("selected_flight")
    passenger_data = session.get("passenger_data")

    if not selected_flight or not passenger_data:
        flash("Please select a flight and enter passenger details first.", "error")
        return redirect(url_for("home"))

    if request.method == "POST":
        selected_seat = request.form.get("seat", "").strip()

        if not selected_seat:
            flash("Please choose a seat before continuing.", "error")
            seat_rows = generate_seat_map(selected_flight)
            return render_template(
                "seat_selection.html",
                flight=selected_flight,
                seat_rows=seat_rows
            )

        booked_seats = get_booked_seats_for_flight(selected_flight)
        permanently_unavailable = {"1A", "1F", "2C", "3D", "4B", "5E", "7A", "8F"}

        if selected_seat in booked_seats or selected_seat in permanently_unavailable:
            flash("That seat is no longer available. Please choose another seat.", "error")
            seat_rows = generate_seat_map(selected_flight)
            return render_template(
                "seat_selection.html",
                flight=selected_flight,
                seat_rows=seat_rows
            )

        session["selected_seat"] = selected_seat
        return redirect(url_for("review_booking"))

    seat_rows = generate_seat_map(selected_flight)
    return render_template(
        "seat_selection.html",
        flight=selected_flight,
        seat_rows=seat_rows
    )


@app.route("/review-booking")
def review_booking():
    selected_flight = session.get("selected_flight")
    passenger_data = session.get("passenger_data")
    selected_seat = session.get("selected_seat")
    search_data = session.get("search_data", {})
    extras = session.get("extras", {})

    if not selected_flight or not passenger_data or not selected_seat:
        flash("Please complete passenger details and seat selection first.", "error")
        return redirect(url_for("home"))

    return render_template(
        "review_booking.html",
        flight=selected_flight,
        passenger=passenger_data,
        selected_seat=selected_seat,
        search_data=search_data,
        extras=extras
    )
@app.route("/extras", methods=["GET", "POST"])
def extras():
    if request.method == "POST":
        baggage = request.form.get("baggage")
        meal_choice = request.form.get("meal_choice")
        insurance = request.form.get("insurance")

        session["extras"] = {
            "baggage": baggage,
            "meal_choice": meal_choice,
            "insurance": insurance
        }

        return redirect(url_for("seat_selection"))

    return render_template("extras.html")

@app.route("/payment", methods=["GET", "POST"])
def payment():
    selected_flight = session.get("selected_flight")
    passenger_data = session.get("passenger_data")
    selected_seat = session.get("selected_seat")
    search_data = session.get("search_data", {})
    extras = session.get("extras", {})

    if not selected_flight or not passenger_data:
        flash("Please select a flight and enter passenger details first.", "error")
        return redirect(url_for("home"))

    if not selected_seat:
        flash("Please choose a seat before payment.", "error")
        return redirect(url_for("seat_selection"))

    if not session.get("user_id"):
        session["post_login_redirect"] = url_for("payment")
        flash("Please log in to complete your booking.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        payment_data = {
            "card_name": request.form.get("card_name", "").strip(),
            "card_number": request.form.get("card_number", "").strip(),
            "expiry_date": request.form.get("expiry_date", "").strip(),
            "cvv": request.form.get("cvv", "").strip()
        }

        if not request.form.get("accept_terms"):
            flash("You must accept the Terms & Conditions before completing your booking.", "error")
            return render_template(
                "payment.html",
                flight=selected_flight,
                passenger=passenger_data,
                selected_seat=selected_seat,
                extras=extras
            )

        if not all(payment_data.values()):
            flash("Please fill in all payment fields.", "error")
            return render_template(
                "payment.html",
                flight=selected_flight,
                passenger=passenger_data,
                selected_seat=selected_seat,
                extras=extras
            )

        booking_reference = generate_booking_reference()
        points_earned = calculate_points(selected_flight["price"])
        flight_date = search_data.get("depart_date", "")

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO bookings (
                user_id,
                booking_reference,
                first_name,
                last_name,
                email,
                phone,
                passport_number,
                airline,
                departure_airport,
                departure_city,
                departure_code,
                destination_airport,
                destination_city,
                destination_code,
                flight_date,
                departure_time,
                arrival_time,
                ticket_class,
                meal_choice,
                seat,
                price,
                points_earned,
                trip_type,
                change_request,
                change_status,
                flight_status,
                extra_baggage,
                priority_boarding,
                wifi_package,
                lounge_access,
                requested_route,
                requested_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            booking_reference,
            passenger_data["first_name"],
            passenger_data["last_name"],
            passenger_data["email"],
            passenger_data["phone"],
            passenger_data["passport_number"],
            selected_flight["airline"],
            selected_flight["from"],
            selected_flight["from_city"],
            selected_flight["from_code"],
            selected_flight["to"],
            selected_flight["to_city"],
            selected_flight["to_code"],
            flight_date,
            selected_flight["departure_time"],
            selected_flight["arrival_time"],
            selected_flight["class"],
            extras.get("meal_choice", "No Meal"),
            selected_seat,
            selected_flight["price"],
            points_earned,
            search_data.get("trip_type", "return"),
            "",
            "None",
            DEFAULT_FLIGHT_STATUS,
            0,
            0,
            0,
            0,
            "",
            ""
        ))
        conn.commit()
        conn.close()

        session["booking_reference"] = booking_reference
        session["points_earned"] = points_earned

        return redirect(url_for("confirmation"))

    return render_template(
        "payment.html",
        flight=selected_flight,
        passenger=passenger_data,
        selected_seat=selected_seat,
        extras=extras
    ) 

@app.route("/confirmation")
def confirmation():
    selected_flight = session.get("selected_flight")
    passenger_data = session.get("passenger_data")
    selected_seat = session.get("selected_seat")
    booking_reference = session.get("booking_reference")
    points_earned = session.get("points_earned", 0)

    if not selected_flight or not passenger_data or not booking_reference:
        flash("No booking confirmation found.", "error")
        return redirect(url_for("home"))

    return render_template(
        "confirmation.html",
        flight=selected_flight,
        passenger=passenger_data,
        selected_seat=selected_seat,
        booking_reference=booking_reference,
        benefits=CLASS_BENEFITS.get(selected_flight["class"], {}),
        points_earned=points_earned
    )


@app.route("/bookings")
def bookings():
    if not session.get("user_id"):
        session["post_login_redirect"] = url_for("bookings")
        flash("Please log in to view and manage your bookings.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    rows = conn.execute("""
        SELECT * FROM bookings
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    total_points = conn.execute("""
        SELECT COALESCE(SUM(points_earned), 0) AS total
        FROM bookings
        WHERE user_id = ?
    """, (session["user_id"],)).fetchone()["total"]

    conn.close()

    enriched_bookings = [enrich_booking_for_display(row) for row in rows]
    tier_info = get_tier_info(total_points)

    return render_template(
        "bookings.html",
        bookings=enriched_bookings,
        total_points=total_points,
        common_meal_options=COMMON_MEAL_OPTIONS,
        tier_info=tier_info,
        extra_prices=EXTRA_PRICES
    )


@app.route("/update-meal/<int:booking_id>", methods=["POST"])
def update_meal(booking_id):
    if not session.get("user_id"):
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    new_meal = request.form.get("meal_choice", "").strip()
    if not new_meal:
        flash("Please choose a meal option.", "error")
        return redirect(url_for("bookings"))

    conn = get_db_connection()
    booking = conn.execute("""
        SELECT id FROM bookings
        WHERE id = ? AND user_id = ?
    """, (booking_id, session["user_id"])).fetchone()

    if not booking:
        conn.close()
        flash("Booking not found.", "error")
        return redirect(url_for("bookings"))

    conn.execute("""
        UPDATE bookings
        SET meal_choice = ?
        WHERE id = ? AND user_id = ?
    """, (new_meal, booking_id, session["user_id"]))
    conn.commit()
    conn.close()

    flash("Meal preference updated successfully.", "success")
    return redirect(url_for("bookings"))


@app.route("/update-extras/<int:booking_id>", methods=["POST"])
def update_extras(booking_id):
    if not session.get("user_id"):
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    extra_baggage = max(0, int(request.form.get("extra_baggage", 0) or 0))
    priority_boarding = 1 if request.form.get("priority_boarding") == "on" else 0
    wifi_package = 1 if request.form.get("wifi_package") == "on" else 0
    lounge_access = 1 if request.form.get("lounge_access") == "on" else 0

    conn = get_db_connection()
    booking = conn.execute("""
        SELECT * FROM bookings
        WHERE id = ? AND user_id = ?
    """, (booking_id, session["user_id"])).fetchone()

    if not booking:
        conn.close()
        flash("Booking not found.", "error")
        return redirect(url_for("bookings"))

    old_extras_total = calculate_extras_total(
        booking["extra_baggage"],
        booking["priority_boarding"],
        booking["wifi_package"],
        booking["lounge_access"]
    )
    new_extras_total = calculate_extras_total(
        extra_baggage,
        priority_boarding,
        wifi_package,
        lounge_access
    )

    new_total_price = booking["price"] - old_extras_total + new_extras_total
    new_points = calculate_points(new_total_price)

    conn.execute("""
        UPDATE bookings
        SET extra_baggage = ?,
            priority_boarding = ?,
            wifi_package = ?,
            lounge_access = ?,
            price = ?,
            points_earned = ?
        WHERE id = ? AND user_id = ?
    """, (
        extra_baggage,
        priority_boarding,
        wifi_package,
        lounge_access,
        new_total_price,
        new_points,
        booking_id,
        session["user_id"]
    ))
    conn.commit()
    conn.close()

    flash("Travel extras updated successfully.", "success")
    return redirect(url_for("bookings"))


@app.route("/upgrade-booking/<int:booking_id>", methods=["POST"])
def upgrade_booking(booking_id):
    if not session.get("user_id"):
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    new_class = request.form.get("new_class", "").strip()

    conn = get_db_connection()
    booking = conn.execute("""
        SELECT * FROM bookings
        WHERE id = ? AND user_id = ?
    """, (booking_id, session["user_id"])).fetchone()

    if not booking:
        conn.close()
        flash("Booking not found.", "error")
        return redirect(url_for("bookings"))

    current_class = booking["ticket_class"]
    valid_upgrades = get_available_upgrades(current_class)

    if new_class not in valid_upgrades:
        conn.close()
        flash("That upgrade option is not available.", "error")
        return redirect(url_for("bookings"))

    extra_cost = valid_upgrades[new_class]
    new_total_price = booking["price"] + extra_cost
    new_points = calculate_points(new_total_price)

    conn.execute("""
        UPDATE bookings
        SET ticket_class = ?, price = ?, points_earned = ?
        WHERE id = ? AND user_id = ?
    """, (
        new_class,
        new_total_price,
        new_points,
        booking_id,
        session["user_id"]
    ))
    conn.commit()
    conn.close()

    flash(f"Booking upgraded to {new_class}. Extra cost: £{extra_cost}. You can update your meal choice if needed.", "success")
    return redirect(url_for("bookings"))


@app.route("/request-change/<int:booking_id>", methods=["POST"])
def request_change(booking_id):
    if not session.get("user_id"):
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    requested_route = request.form.get("requested_route", "").strip()
    requested_date = request.form.get("requested_date", "").strip()
    request_reason = request.form.get("request_reason", "").strip()

    if not requested_route and not requested_date and not request_reason:
        flash("Please enter at least one change request detail.", "error")
        return redirect(url_for("bookings"))

    request_summary = (
        f"Requested Route: {requested_route or 'No change specified'} | "
        f"Requested Date: {requested_date or 'No date specified'} | "
        f"Reason: {request_reason or 'No reason given'}"
    )

    conn = get_db_connection()
    booking = conn.execute("""
        SELECT id FROM bookings
        WHERE id = ? AND user_id = ?
    """, (booking_id, session["user_id"])).fetchone()

    if not booking:
        conn.close()
        flash("Booking not found.", "error")
        return redirect(url_for("bookings"))

    conn.execute("""
        UPDATE bookings
        SET change_request = ?,
            change_status = ?,
            requested_route = ?,
            requested_date = ?
        WHERE id = ? AND user_id = ?
    """, (
        request_summary,
        "Pending",
        requested_route,
        requested_date,
        booking_id,
        session["user_id"]
    ))
    conn.commit()
    conn.close()

    flash("Flight change request submitted.", "success")
    return redirect(url_for("bookings"))


@app.route("/boarding-pass/<int:booking_id>")
def boarding_pass(booking_id):
    if not session.get("user_id"):
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    booking = conn.execute("""
        SELECT * FROM bookings
        WHERE id = ? AND user_id = ?
    """, (booking_id, session["user_id"])).fetchone()
    conn.close()

    if not booking:
        flash("Boarding pass not found.", "error")
        return redirect(url_for("bookings"))

    return render_template("boarding_pass.html", booking=booking)


@app.route("/cancel-booking/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):
    if not session.get("user_id"):
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    conn.execute("""
        DELETE FROM bookings
        WHERE id = ? AND user_id = ?
    """, (booking_id, session["user_id"]))
    conn.commit()
    conn.close()

    flash("Booking cancelled successfully.", "success")
    return redirect(url_for("bookings"))


@app.route("/admin")
def admin_dashboard():
    if not is_admin():
        flash("Admin access only.", "error")
        return redirect(url_for("home"))

    conn = get_db_connection()
    rows = conn.execute("""
        SELECT bookings.*, users.full_name AS account_name
        FROM bookings
        JOIN users ON bookings.user_id = users.id
        ORDER BY bookings.id DESC
    """).fetchall()
    conn.close()

    bookings = [enrich_booking_for_display(row) for row in rows]

    return render_template(
        "admin.html",
        bookings=bookings,
        flight_status_options=[
            "Scheduled",
            "Boarding",
            "Delayed",
            "Departed",
            "Cancelled"
        ]
    )


@app.route("/admin/update-change-status/<int:booking_id>", methods=["POST"])
def admin_update_change_status(booking_id):
    if not is_admin():
        flash("Admin access only.", "error")
        return redirect(url_for("home"))

    new_status = request.form.get("change_status", "").strip()
    if new_status not in ["Pending", "Approved", "Rejected"]:
        flash("Invalid change status.", "error")
        return redirect(url_for("admin_dashboard"))

    conn = get_db_connection()
    booking = conn.execute("""
        SELECT * FROM bookings
        WHERE id = ?
    """, (booking_id,)).fetchone()

    if not booking:
        conn.close()
        flash("Booking not found.", "error")
        return redirect(url_for("admin_dashboard"))

    conn.execute("""
        UPDATE bookings
        SET change_status = ?
        WHERE id = ?
    """, (new_status, booking_id))

    if new_status == "Approved":
        apply_approved_change_to_booking(conn, booking)

    conn.commit()
    conn.close()

    flash("Change request status updated.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/update-flight-status/<int:booking_id>", methods=["POST"])
def admin_update_flight_status(booking_id):
    if not is_admin():
        flash("Admin access only.", "error")
        return redirect(url_for("home"))

    new_status = request.form.get("flight_status", "").strip()
    valid_statuses = ["Scheduled", "Boarding", "Delayed", "Departed", "Cancelled"]

    if new_status not in valid_statuses:
        flash("Invalid flight status.", "error")
        return redirect(url_for("admin_dashboard"))

    conn = get_db_connection()
    conn.execute("""
        UPDATE bookings
        SET flight_status = ?
        WHERE id = ?
    """, (new_status, booking_id))
    conn.commit()
    conn.close()

    flash("Flight status updated.", "success")
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)