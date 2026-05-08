from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from dotenv import load_dotenv
import os
load_dotenv()
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
import random
import string
import sqlite3
import os
import csv
import re
import unicodedata
import requests
import time
import hashlib


EXCHANGE_RATES = {"GBP": 1}
LAST_FETCH = 0
CACHE_DURATION = 3600 


app = Flask(__name__)
app.secret_key = "super_secret_key_change_this_later"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "bookings.db")
translations = {
    "en": {
        "welcome": "Welcome to AirGo",
        "subtitle": "Book and manage your flights directly with our airline",
        "search": "Search Flights",
        "manage_booking": "Manage Booking",
        "admin": "Admin",
        "logout": "Logout",
        "login": "Login",
        "signup": "Sign Up",
        "search_currency": "Search currency...",

        "trip_type": "Trip Type",
        "from_label": "From",
        "to_label": "To",
        "departure_date": "Departure Date",
        "return_date": "Return Date",
        "second_flight": "Second Flight",
        "passengers": "Passengers",
        "class_label": "Class",
        "example_departure": "Departure Airport",
        "example_arrival": "Arrival Airport",

        "return_trip": "Return",
        "one_way": "One Way",
        "multi_city": "Multi City",

        "popular_routes": "Popular routes",
        "explore_destinations": "Explore our most booked destinations",
        "choose_destination": "Choose a destination to fill your search instantly and start booking faster.",
        "uk": "United Kingdom",
        "usa": "United States",
        "tr": "Türkiye",
        "lba": "Leeds",
        "jfk": "New York",
        "ist": "Istanbul",

        "passenger_details_title": "Passenger Details",
        "selected_flight": "Selected Flight",
        "whats_included": "What’s Included With",
        "first_name": "First Name",
        "last_name": "Last Name",
        "email_address": "Email Address",
        "phone_number": "Phone Number",
        "passport_number": "Passport Number",

        "baggage": "Baggage",
        "meal": "Meal",
        "seat_selection": "Seat Selection",
        "lounge": "Lounge",
        "flexibility": "Flexibility",

        "assistance_title": "Accessibility & Special Assistance",
        "assistance_text": "This service is provided at no extra cost. Let us know if you need any support during your journey.",
        "assistance_required": "I require special assistance",
        "other_assistance": "Other assistance needs",
        "other_assistance_placeholder": "Please describe any other support you may need",

        "wheelchair_assistance": "Wheelchair assistance",
        "visual_assistance": "Visual assistance",
        "hearing_assistance": "Hearing assistance",
        "pregnancy_support": "Pregnancy support",
        "travelling_with_infant": "Travelling with infant",
        "elderly_support": "Elderly passenger support",
        "medical_assistance": "Medical assistance",
        "extra_boarding_time": "Extra boarding time",
        "airport_security_assistance": "Airport/security assistance",
        "special_seating_request": "Special seating request",

        "extras_title": "Choose Your Extras",
        "extras_subtitle": "Select any extras for your trip before continuing.",
        "your_flight": "Your Flight",
        "airline": "Airline",
        "route": "Route",
        "base_price": "Base Price",

        "continue_to_extras": "Continue to Extras",

        "review_title": "Review Your Booking",
        "review_subtitle": "Please review your flight, passenger details, and selected extras before continuing to payment.",
        "flight_details": "Flight Details",
        "date": "Date",
        "time": "Time",
        "departure": "Departure",
        "arrival": "Arrival",
        "back_manage_booking": "Back to Manage Booking",
        "seat": "Seat",
        "selected_extras": "Selected Extras",
        "name": "Name",
        "no_baggage": "No extra baggage",
        "no_insurance": "No Travel Insurance",
        "back": "Back",
        "continue_payment": "Continue to Payment",

        "payment_title": "Payment",
        "fare_details": "Fare Details",
        "includes_taxes": "includes taxes & fees",
        "total": "Total",
        "booking_summary": "Booking Summary",
        "passenger_label": "Passenger",
        "flight_label": "Flight",
        "name_on_card": "Name on Card",
        "card_number": "Card Number",
        "expiry_date": "Expiry Date",
        "expiry_placeholder": "MM/YY",
        "cvv": "CVV",
        "agree_terms_1": "I agree to the",
        "terms_conditions": "Terms & Conditions",
        "receive_offers": "I would like to receive offers and updates",
        "complete_booking": "Complete Booking",

        "booking_terms": "Booking Terms",
        "booking_terms_text": "By completing a booking with AirGo, you confirm that all passenger details provided are accurate and complete.",
        "payments": "Payments",
        "payments_text": "All payments must be completed in full before a booking is confirmed. Prices shown at checkout include the selected flight and chosen extras.",
        "changes_cancellations": "Changes and Cancellations",
        "changes_cancellations_text": "Changes and cancellations are subject to the fare type and airline policy. Additional fees may apply depending on the request.",
        "passenger_responsibility": "Passenger Responsibility",
        "passenger_responsibility_text": "Passengers are responsible for ensuring they have valid travel documents, including passports, visas, and any required identification.",
        "special_requests": "Special Requests",
        "special_requests_text": "Requests such as meal preferences, assistance, and baggage selections will be recorded, but some services remain subject to availability.",
        "notifications_offers": "Notifications and Offers",
        "notifications_offers_text": "If you choose to receive updates and promotions, AirGo may contact you by email with booking updates, offers, and service information",
        "confirmation_page_title": "Booking Confirmation",
"booking_confirmed": "Booking Confirmed",
"booking_success_message": "Your flight has been booked successfully",
"booking_reference": "Booking Reference",
"email_label": "Email",
"departure_time_label": "Departure Time",
"arrival_time_label": "Arrival Time",
"ticket_class_label": "Ticket Class",
"total_paid": "Total Paid",
"points_earned": "points earned",
"book_another_flight": "Book Another Flight",
"manage_my_bookings": "Manage My Bookings",
"manage_subtitle": "View and manage your bookings",
"total_points": "Total Points",
"current_tier": "Current Tier",
"points_to": "points to",
"highest_tier": "You are already at the highest tier",
"flight_status": "Flight Status",
"change_status": "Change Status",
"latest_request": "Latest Request",
"update_meal": "Update Meal",
"save": "Save",
"upgrade_cabin": "Upgrade Cabin",
"upgrade": "Upgrade",
"no_upgrade": "No upgrades available",
"travel_extras": "Travel Extras",
"extra_baggage": "Extra Baggage",
"priority_boarding": "Priority Boarding",
"wifi": "Wi-Fi",
"request_change": "Request Change",
"new_departure": "New Departure",
"new_destination": "New Destination",
"new_date": "New Date",
"reason": "Reason",
"submit_request": "Submit Request",
"view_boarding_pass": "View Boarding Pass",
"cancel_booking": "Cancel Booking",
"no_bookings": "You do not have any bookings yet",
"available_flights": "Available Flights",
"to_connector": "to",
"on_date": "on",
"from_price": "From",
"seats_left": "seats left",
"direct_flight": "Direct flight",
"cabin_bag_included": "Cabin bag included",
"seat_selection_available": "Seat selection available",
"select_flight": "Select Flight",
"back_to_search": "Back to Search",
"economy": "Economy",
"premium_economy": "Premium Economy",
"business": "Business",
"first_class": "First",
"password": "Password",
"no_account": "Don’t have an account?",
"create_one": "Create one",
"forgot_password": "Forgot password?",
"create_account": "Create Account",
"full_name": "Full Name",
"already_account": "Already have an account?",
"forgot_password_title": "Forgot Password",
"reset_password": "Reset Password",
"account_email": "Account Email",
"new_password": "New Password",
"confirm_new_password": "Confirm New Password",
"update_password": "Update Password",
"back_to_login": "Back to login",
"boarding_pass": "Boarding Pass",
"boarding_gate": "Gate",
"boarding_group": "Group",
"not_assigned": "Not Assigned",
"print_boarding_pass": "Print Boarding Pass",
"no_exact_matches": "No exact matches found. Showing sample flights instead.",
"any_class": "Any",
"class_economy": "Economy",
"class_premium": "Premium Economy",
"class_business": "Business",
"class_first": "First",

"benefit_cabin_bag_1": "1 cabin bag",
"benefit_cabin_bag_checked_1": "1 cabin bag + 1 checked bag",
"benefit_checked_bags_2_cabin_1": "2 checked bags + 1 cabin bag",
"benefit_checked_bags_3_cabin_2": "3 checked bags + 2 cabin bags",

"benefit_standard_meal": "Standard meal",
"benefit_premium_meal": "Premium meal",
"benefit_business_dining": "Business class dining",
"benefit_first_dining": "First class dining",

"benefit_standard_seat_selection": "Standard seat selection",
"benefit_included": "Included",
"benefit_priority_seat_selection": "Priority seat selection",
"benefit_luxury_suite_selection": "Luxury suite selection",

"benefit_not_included": "Not included",

"benefit_low_flexibility": "Low flexibility",
"benefit_medium_flexibility": "Medium flexibility",
"benefit_high_flexibility": "High flexibility",
"benefit_maximum_flexibility": "Maximum flexibility",

"price_label": "Price",
"airline_label": "Airline",
"add_another_flight": "Add Another Flight",
"top_choice": "Top Choice",
"popular_in_uk": "Popular in UK",
"long_haul_favourite": "Long-haul favourite",
"flight": "Flight",
"remove_flight": "Remove Flight",
"selected_seats": "Selected seats",

"search_hotels": "Search Hotels",
"destination_city": "Destination City",
"where_to": "Where to?",
"check_in": "Check In",
"check_out": "Check Out",
"number_of_guests": "Number of Guests",
"guest": "Guest",
"guests": "Guests",
"no_cities_found": "No cities found",
"city_error": "Could not load cities",
"select_city_alert": "Please select a city from the suggestions",

"hotel_results_title": "Hotel Results",
"available_hotels_in": "Available Hotels in",
"night": "Night",
"nights": "Nights",
"price_per_night": "Price per night",
"book_hotel": "Book Hotel",
"no_hotels_found": "No hotels found for this destination.",
"try_another_search": "Try another search",

"location": "Location",
"booking_details": "Booking Details",
"room_type": "Room Type",
"total_price": "Total Price",
"booking_payment_message": "By clicking confirm, your booking will be charged using your account payment method.",
"confirm_booking": "Confirm Booking",
"back_to_results": "Back to results",

"hotel_booking_confirmed": "Hotel Booking Confirmed",
"hotel_success_message": "Your hotel has been booked successfully",
"booking_reference": "Booking Reference",
"hotel": "Hotel",
"total_paid": "Total Paid",
"status": "Status",
"linked_booking": "This hotel booking is linked to your flight booking.",
"view_linked_flight": "View linked flight booking",
"view_all_bookings": "View All My Bookings",
"back_home": "Back to Home",

"flight_tracker_title": "Flight Tracker",
"flight_tracker": "Flight Tracker",
"enter_reference": "Enter your booking reference to track your flight status.",
"example_reference": "e.g. ABC12345",
"track_flight": "Track Flight",
"no_booking_found": "No booking found with that reference. Please check and try again.",
"flight_date": "Flight Date",
"departure": "Departure",
"arrival": "Arrival",
"airline": "Airline",
"flight_cancelled": "Flight Cancelled",
"flight_delayed": "Flight Delayed — check back for updates",
"current_status": "Current Status",

"no_flights_found": "No flights found",
"no_flights_text": "We couldn't find any flights matching your search. Try adjusting your search criteria or check back later.",

"hotels": "Hotels",
"track_flight": "Track Flight",

"passengers": "Passengers",
"seat": "Seat",
"refund_status": "Refund Status",
"select_passengers": "Select passengers",
"update_meal": "Update Meal",
"save_meal": "Save Meal",
"travel_extras": "Travel Extras",
"save_extras": "Save Extras",
"upgrade_cabin": "Upgrade Cabin",
"available_upgrades": "Available Upgrades",
"upgrade_passenger": "Upgrade This Passenger",
"request_refund": "Request Refund",
"reason_refund": "Reason for refund",
"flights": "Flights",
"refund_status": "Refund Status",
"refund_amount": "Refund Amount",
"requested_refund": "Requested Refund",
"passengers_requested": "Passengers Requested",
"remaining_passengers": "Remaining Passengers",
"request_refund": "Request Refund",
"request_hotel_refund": "Request Hotel Refund",
"request_date_change": "Request Date Change",
"reason_refund": "Reason for refund",
"select_passenger_refund": "Select passenger to refund",
"other_reason": "Other reason",
"submit_refund_request": "Submit Refund Request",
"submit_hotel_refund_request": "Submit Hotel Refund Request",
"submit_change_request": "Submit Change Request",
"hotel_bookings": "Hotel Bookings",
"hotel_booking": "Hotel Booking",
"hotel": "Hotel",
"check_in": "Check In",
"check_out": "Check Out",
"guests": "Guests",
"status": "Status",
"new_check_in": "New Check In",
"new_check_out": "New Check Out",
"requested_dates": "Requested Dates",
"refund_pending": "Refund request pending.",
"refund_approved": "Refund approved.",
"refund_rejected": "Refund rejected.",
"date_change_pending": "Change request pending.",
"date_change_approved": "Date change approved.",
"date_change_rejected": "Date change rejected.",
"hotel_cancelled_note": "Date changes are unavailable because this hotel booking is cancelled.",
"hotel_refund_pending_note": "Date changes are unavailable while your refund request is pending.",
"need_hotel": "Need a hotel for this trip?",
"find_hotels_in": "Find hotels in",
"no_bookings_yet": "No bookings yet",
"no_bookings_text": "You haven't made any bookings yet. Search for flights to book your first trip.",
"change_plans": "Change of plans",
"found_cheaper_flight": "Found cheaper flight",
"found_cheaper_hotel": "Found cheaper hotel",
"medical_reason": "Medical reason",
"visa_passport_issue": "Visa/passport issue",
"airline_schedule_issue": "Airline schedule issue",
"travel_disruption": "Travel disruption",
"flight_cancelled_changed": "Flight cancelled or changed",
"other": "Other",
"only_fill_other": "Only fill this in if you selected Other",
"cancelled": "Cancelled",
"changed": "Changed",
"active": "Active",
"cabin": "Cabin",
"no_checked_bag": "No checked bag",
"one_checked_bag": "1 checked bag",
"two_checked_bags": "2 checked bags",
"lounge_access": "Lounge Access",
"available_upgrades": "Available Upgrades",
"upgrade_passenger": "Upgrade This Passenger",
"no_upgrades_passenger": "No upgrades available for this passenger.",
"Vegetarian Meal": "Vegetarian Meal",
"Vegan Meal": "Vegan Meal",
"Halal Meal": "Halal Meal",
"Standard Meal": "Standard Meal",
"Gluten Free Meal": "Gluten Free Meal",
"No Meal": "No Meal",
"Economy": "Economy",
"Premium Economy": "Premium Economy",
"Business": "Business",
"First": "First",
"Cancelled": "Cancelled",
"Approved": "Approved",
"Rejected": "Rejected",
"Pending": "Pending",
"Active": "Active",
"Changed": "Changed",
"No checked bag": "No checked bag",
"1 checked bag": "1 checked bag",
"2 checked bags": "2 checked bags",
"Change of plans": "Change of plans",
"Found cheaper flight": "Found cheaper flight",
"Found cheaper hotel": "Found cheaper hotel",
"Medical reason": "Medical reason",
"Visa/passport issue": "Visa/passport issue",
"Airline schedule issue": "Airline schedule issue",
"Travel disruption": "Travel disruption",
"Flight cancelled or changed": "Flight cancelled or changed",
"Other": "Other",
"CONFIRMED": "CONFIRMED",

"airgo_rewards": "AirGo Rewards",
"use_points": "Use Points",
"available_points": "Available Points",
"discount": "discount",
"off": "OFF",
"pay_full_price": "Pay full price",

"base_fares": "Base fares",
"seat_selection_price": "Seat selection",
"points": "points",
"your_points": "Your points",
"no_points": "No points",
"secure_checkout": "Secure Checkout",
"secure_payment_text": "Secure payment protected by AirGo",

"airport_transfers": "Airport Transfers",
"book_transfer_between": "Book a transfer between an airport and your destination address.",
"airport_to_address": "Airport → Address",
"address_to_airport": "Address → Airport",
"from_airport": "From — Airport",
"to_airport": "To — Airport",
"destination_address": "To — Destination Address",
"your_address": "From — Your Address",
"address_line_1": "Address Line 1",
"address_line_2": "Address Line 2 (optional)",
"town_city": "Town / City",
"postcode": "Postcode",
"county": "County",
"country": "Country",
"transfer_type": "Transfer Type",
"search_transfers": "Search Transfers",
"distance": "Distance",
"estimated_travel_time": "Estimated Travel Time",
"available_transfers": "Available Transfers",
"travel_time": "Travel Time",
"estimated_price": "Estimated price",
"book_now": "Book",
"search_again": "Search again",
"loading_map": "Loading map...",
"map_unavailable": "Map unavailable in this environment.",
"passenger_details": "Passenger Details",
"confirm_transfer_details": "Confirm your details for the transfer booking.",
"first_name": "First Name",
"last_name": "Last Name",
"email_address": "Email Address",
"mobile_number": "Mobile Number",
"alternative_number": "Alternative Number",
"optional": "optional",
"special_requests": "Special Requests",
"continue_payment": "Continue to Payment",
"name_on_card": "Name on Card",
"card_number": "Card Number",
"expiry_date": "Expiry Date",
"complete_booking": "Complete Booking",
"booking_summary": "Booking Summary",
"pickup": "Pickup",
"dropoff": "Dropoff",
"total": "Total",
"fare_details": "Fare Details",
"use_points": "Use Points",
"your_points": "Your points",
"points_discount": "Points discount",
"no_points": "No points",
"pay_full_price": "Pay full price",
"booking_confirmed": "Booking Confirmed",
"transfer_booked": "Transfer Booked!",
"transfer_confirmed": "Your airport transfer has been confirmed.",
"booking_reference": "Booking Reference",
"transfer_details": "Transfer Details",
"transfer_type_label": "Transfer Type",
"total_paid": "Total Paid",
"view_bookings": "View My Bookings",
"back_home": "Back to Home",
"standard_taxi": "Standard Taxi",
"up_to_4_passengers": "up to 4 passengers",

"need_login_transfer": "You need to log in before you can book a transfer.",
"premium": "PREMIUM",
"exclusive": "EXCLUSIVE",
"no_transfer_options": "No transfer options available.",
"map_route_unavailable": "Map unavailable — route could not be calculated.",
"standard_taxi_expect": "What to expect with Standard Taxi",
"minivan_expect": "What to expect with Minivan",
"luxury_car_expect": "What to expect with Luxury Car",
"meet_greet_expect": "What to expect with Meet & Greet + Luxury Transfer",
"standard_taxi_point_1": "🧳 You load your own luggage into the boot",
"standard_taxi_point_2": "🚗 Clean, comfortable saloon car — Toyota Prius or similar",
"standard_taxi_point_3": "👤 Up to 4 passengers",
"standard_taxi_point_4": "📱 Driver will contact you on arrival",
"standard_taxi_point_5": "💳 Pay by card or cash at the end of the journey",
"standard_taxi_point_6": "⏱ Driver waits up to 15 minutes at no extra charge",
"standard_taxi_point_7": "🌡 Air conditioning included",
"standard_taxi_point_8": "🚫 No refreshments provided",
"minivan_point_1": "👨‍👩‍👧‍👦 Best option for groups of 5 or more",
"minivan_point_2": "🚐 Spacious Ford Tourneo or similar — seats up to 7",
"minivan_point_3": "🧳 Large luggage capacity — no need to squash bags",
"minivan_point_4": "🥤 Complimentary welcome drink for all passengers",
"minivan_point_5": "🌡 Full climate control throughout the journey",
"minivan_point_6": "🎵 In-vehicle entertainment system available",
"minivan_point_7": "💺 Wide, comfortable seats with extra legroom",
"minivan_point_8": "📱 Driver meets you at arrivals with a name board",
"luxury_car_point_1": "🚘 Mercedes S-Class or BMW 7 Series — immaculate condition",
"luxury_car_point_2": "👔 Professionally suited chauffeur",
"luxury_car_point_3": "🧳 Chauffeur handles all your luggage",
"luxury_car_point_4": "🥂 Chilled water and mints provided",
"luxury_car_point_5": "📰 Newspapers and magazines available on request",
"luxury_car_point_6": "🔇 Quiet, private cabin — perfect for business calls",
"luxury_car_point_7": "🌡 Personalised climate control",
"luxury_car_point_8": "📱 Chauffeur meets you inside the terminal",
"meet_greet_point_1": "✈ Representative meets you at the gate as you step off the plane",
"meet_greet_point_2": "🛂 Fast track through immigration and security",
"meet_greet_point_3": "🧳 Dedicated porter carries all your luggage",
"meet_greet_point_4": "🚐 Mercedes V-Class waiting at the terminal exit — up to 7 passengers",
"meet_greet_point_5": "🥂 Champagne or premium soft drinks on arrival",
"meet_greet_point_6": "📋 All travel documentation handled for you",
"meet_greet_point_7": "🏨 Can arrange hotel check-in coordination on request",
"meet_greet_point_8": "📞 24/7 concierge support throughout your journey",
"transfer_details": "Transfer Details",
"complete_transfer_booking": "Complete your airport transfer booking.",
"full_name": "Full Name",
"phone_number": "Phone Number",
"flight_number": "Flight Number",
"pickup_date": "Pickup Date",
"pickup_time": "Pickup Time",
"luggage": "Luggage",
"special_requests": "Special Requests",
"special_requests_placeholder": "Add any requests or important details...",
"continue_to_payment": "Continue to Payment",

"fare_details": "Fare Details",
"transfer_type": "Transfer",
"distance": "Distance",
"travel_time": "Travel Time",
"points_discount": "Points discount",
"total": "Total",
"use_points": "Use Points",
"your_points": "Your points",
"points": "points",
"discount": "discount",
"off": "off",
"no_points": "No points",
"pay_full_price": "Pay full price",
"booking_summary": "Booking Summary",
"passenger_label": "Passenger",
"phone_number": "Phone",
"alternative_number": "Alt Phone",
"pickup": "Pickup",
"dropoff": "Dropoff",
"name_on_card": "Name on Card",
"card_number": "Card Number",
"expiry_date": "Expiry Date",
"receive_offers": "I would like to receive offers and updates",
"complete_booking": "Complete Booking",
"i_agree_terms": "I agree to the",
"terms_conditions": "Terms & Conditions",
"booking_terms": "Booking Terms",
"payments": "Payments",
"changes_cancellations": "Changes and Cancellations",
"passenger_responsibility": "Passenger Responsibility",

"booking_terms_text": "By completing a booking with AirGo, you confirm that all passenger details provided are accurate and complete.",

"payments_text": "All payments must be completed in full before a booking is confirmed.",

"changes_cancellations_text": "Changes and cancellations are subject to the transfer type and may incur additional fees.",

"passenger_responsibility_text": "Passengers are responsible for being ready at the agreed pickup location at the correct time.",
"transfer_booked": "Transfer Booked!",
"transfer_confirmed": "Your airport transfer has been confirmed.",
"view_bookings": "View My Bookings",
"taxis": "Taxis",

"hotel_payment": "Hotel Payment",
"hotel_fare_details": "Hotel Fare Details",
"hotel": "Hotel",
"location": "Location",
"check_in": "Check In",
"check_out": "Check Out",
"guests": "Guests",
"room_type": "Room Type",
"points_discount": "Points discount",
"total": "Total",
"use_points": "Use Points",
"your_points": "Your points",
"points": "points",
"discount": "discount",
"off": "off",
"no_points": "No points",
"pay_full_price": "Pay full price",
"name_on_card": "Name on Card",
"card_number": "Card Number",
"expiry_date": "Expiry Date",
"name_letters_only": "Name must only contain letters",
"card_number_validation": "Card number must be exactly 16 digits",
"cvv_validation": "CVV must be 3 or 4 digits",
"i_agree_terms": "I agree to the",
"terms_conditions": "Terms & Conditions",
"receive_offers": "I would like to receive offers and updates",
"complete_hotel_booking": "Complete Hotel Booking",
"airport_transfers": "Airport Transfers",
"date_booked": "Date Booked",
"price_paid": "Price Paid",
"None": "Confirmed",

"minivan": "Minivan",
"luxury_car": "Luxury Car",
"mercedes_s_class": "Mercedes S-Class",
"meet_greet_luxury_transfer": "Meet & Greet + Luxury Transfer",

"minute": "min",
"minutes": "mins",
<<<<<<< HEAD
"enter_details_for_all": "Enter details for all",
"selected_flights": "Selected Flights",
"choose_seats_for_each_flight_start": "Choose",
"for_each_flight": "for each flight.",
"plural_s": "s",
"seats_for": "Seats for",
"please_choose_seats_alert": "Please choose seats for every flight before continuing. Passengers:",
=======
"need_transfer": "Need a transfer from the airport?",
"transfer_suggestion_text": "Book a taxi or luxury transfer to your destination.",
"book_airport_transfer": "Book Airport Transfer",
"need_hotel_in": "Need a hotel in",
"hotel_suggestion_text": "Find available hotels matching your travel dates at your destination.",
"find_hotels_for_trip": "Find hotels for this trip",
"guest_details": "Guest Details",
"hotel_guest_details_subtitle": "Enter details for all guests staying at the hotel.",
"guest_special_requests": "Guest Special Requests",
"guest_special_requests_placeholder": "Add any requests for this guest...",
"continue_to_hotel_payment": "Continue to Hotel Payment",
"continue_guest_details": "Continue to Guest Details",
"selected_flights": "Selected Flights",
"seats_for": "Seats For",
"per_passenger": "Per Passenger",
<<<<<<< HEAD
"scheduled": "Scheduled",
"boarding": "Boarding",
"departed": "Departed",
"landed": "Landed",
"total_stay_price": "Total stay price",
=======
>>>>>>> 4b446d46dc475c3831deb317bcd77dae800f209c
>>>>>>> b7aa1d88ca5ad71568b2755e0c90c1c795c2d72e
    },
    "fr": {
    "welcome": "Bienvenue sur AirGo",
    "subtitle": "Réservez et gérez vos vols directement avec notre compagnie",
    "search": "Rechercher des vols",
    "manage_booking": "Gérer la réservation",
    "admin": "Admin",
    "logout": "Déconnexion",
    "login": "Connexion",
    "signup": "S’inscrire",
    "search_currency": "Rechercher une devise...",

    "trip_type": "Type de voyage",
    "from_label": "Départ",
    "to_label": "Destination",
    "departure_date": "Date de départ",
    "return_date": "Date de retour",
    "second_flight": "Deuxième vol",
    "passengers": "Passagers",
    "class_label": "Classe",
    "example_departure": "Aéroport de départ",
    "example_arrival": "Aéroport d’arrivée",

    "return_trip": "Aller-retour",
    "one_way": "Aller simple",
    "multi_city": "Multi-destinations",

    "popular_routes": "Routes populaires",
    "explore_destinations": "Découvrez nos destinations les plus réservées",
    "choose_destination": "Choisissez une destination pour remplir votre recherche plus rapidement.",
    "uk": "Royaume-Uni",
    "usa": "États-Unis",
    "tr": "Turqie",
    "lba": "Leeds",
    "jfk": "New York",
    "ist": "Istanbul",

    "passenger_details_title": "Détails du passager",
    "selected_flight": "Vol sélectionné",
    "whats_included": "Ce qui est inclus avec",
    "first_name": "Prénom",
    "last_name": "Nom de famille",
    "email_address": "Adresse e-mail",
    "phone_number": "Numéro de téléphone",
    "passport_number": "Numéro de passeport",

    "baggage": "Bagages",
    "meal": "Repas",
    "seat_selection": "Sélection du siège",
    "lounge": "Salon",
    "flexibility": "Flexibilité",

    "assistance_title": "Accessibilité et assistance spéciale",
    "assistance_text": "Ce service est fourni sans frais supplémentaires. Indiquez-nous si vous avez besoin d’une assistance pendant votre voyage.",
    "assistance_required": "J’ai besoin d’une assistance spéciale",
    "other_assistance": "Autres besoins d’assistance",
    "other_assistance_placeholder": "Veuillez décrire toute autre aide dont vous pourriez avoir besoin",

    "wheelchair_assistance": "Assistance fauteuil roulant",
    "visual_assistance": "Assistance visuelle",
    "hearing_assistance": "Assistance auditive",
    "pregnancy_support": "Assistance grossesse",
    "travelling_with_infant": "Voyage avec un nourrisson",
    "elderly_support": "Assistance passager âgé",
    "medical_assistance": "Assistance médicale",
    "extra_boarding_time": "Temps d’embarquement supplémentaire",
    "airport_security_assistance": "Assistance aéroport/sécurité",
    "special_seating_request": "Demande de siège spécial",

    "extras_title": "Choisissez vos extras",
    "extras_subtitle": "Sélectionnez les extras pour votre voyage avant de continuer.",
    "your_flight": "Votre vol",
    "airline": "Compagnie",
    "route": "Itinéraire",
    "base_price": "Prix de base",
    "baggage_options": "Options de bagages",
    "checked_baggage": "Bagage en soute",
    "no_checked_bag": "Aucun bagage en soute",
    "one_checked_bag": "1 bagage en soute",
    "two_checked_bags": "2 bagages en soute",
    "meal_preference": "Préférence de repas",
    "choose_your_meal": "Choisissez votre repas",
    "standard_meal": "Repas standard",
    "halal_meal": "Repas halal",
    "vegetarian_meal": "Repas végétarien",
    "vegan_meal": "Repas végétalien",
    "gluten_free_meal": "Repas sans gluten",
    "no_meal": "Aucun repas",
    "travel_insurance": "Assurance voyage",
    "insurance_text": "Protégez votre voyage avec une couverture optionnelle avant de payer.",
    "recommended": "Recommandé",
    "travel_protection": "Protection voyage AirGo",
    "only_per_booking": "Seulement",
    "per_booking": "par réservation",
    "insurance_benefit_1": "Modification du vol jusqu’à 24 heures avant le départ",
    "insurance_benefit_2": "Assistance en cas de retard et de perturbation",
    "insurance_benefit_3": "Assistance d’urgence en voyage si nécessaire",
    "insurance_benefit_4": "Plus de flexibilité et de tranquillité d’esprit",
    "add_travel_insurance": "Ajouter l’assurance voyage",
    "continue_without_insurance": "Non, continuer sans assurance",
    "continue_to_seat_selection": "Continuer vers la sélection du siège",

    "seat_selection_title": "Sélection des sièges",
    "choose_seat": "Choisissez votre siège",
    "choose_seat_subtitle": "Choisissez votre zone et votre siège.",
    "seat_prices": "Prix des sièges",
    "window_seat": "Siège fenêtre",
    "aisle_seat": "Siège couloir",
    "middle_seat": "Siège central",
    "exit_seat": "Siège sortie de secours",
    "extra_legroom": "plus d’espace pour les jambes",
    "no_selection": "Pas de sélection",
    "random_seat": "siège attribué aléatoirement",
    "available": "Disponible",
    "unavailable": "Indisponible",
    "selected": "Sélectionné",
    "selected_seat": "Siège sélectionné",
    "seat_type": "Type de siège",
    "seat_price": "Prix du siège",
    "continue_review": "Continuer vers le résumé",
    "none": "Aucun",
    "time": "Heure",
    "fare": "Tarif",

    "continue_to_extras": "Continuer vers les extras",
    "review_title": "Vérifiez votre réservation",
    "review_subtitle": "Veuillez vérifier votre vol, vos informations passager et les extras avant de continuer.",
    "flight_details": "Détails du vol",
    "date": "Date",
    "departure": "Départ",
    "arrival": "Arrivée",
    "seat": "Siège",
    "selected_extras": "Extras sélectionnés",
    "name": "Nom",
    "no_baggage": "Aucun bagage supplémentaire",
    "no_insurance": "Pas d’assurance voyage",
    "back": "Retour",
    "continue_payment": "Continuer vers le paiement",

    "payment_title": "Paiement",
    "fare_details": "Détails du tarif",
    "includes_taxes": "taxes et frais inclus",
    "total": "Total",
    "booking_summary": "Résumé de la réservation",
    "passenger_label": "Passager",
    "flight_label": "Vol",
    "name_on_card": "Nom sur la carte",
    "card_number": "Numéro de carte",
    "expiry_date": "Date d’expiration",
    "expiry_placeholder": "MM/AA",
    "cvv": "CVV",
    "agree_terms_1": "J’accepte les",
    "terms_conditions": "Conditions générales",
    "receive_offers": "Je souhaite recevoir des offres et des mises à jour",
    "complete_booking": "Finaliser la réservation",
    "booking_terms": "Conditions de réservation",
    "booking_terms_text": "En finalisant une réservation avec AirGo, vous confirmez que toutes les informations passager fournies sont exactes et complètes.",
    "payments": "Paiements",
    "payments_text": "Tous les paiements doivent être effectués intégralement avant qu’une réservation soit confirmée. Les prix affichés incluent le vol sélectionné et les extras choisis.",
    "changes_cancellations": "Modifications et annulations",
    "changes_cancellations_text": "Les modifications et annulations dépendent du type de tarif et de la politique de la compagnie. Des frais supplémentaires peuvent s’appliquer.",
    "passenger_responsibility": "Responsabilité du passager",
    "passenger_responsibility_text": "Les passagers sont responsables de s’assurer qu’ils disposent de documents de voyage valides, y compris passeports, visas et toute pièce d’identité requise.",
    "special_requests": "Demandes spéciales",
    "special_requests_text": "Les demandes telles que les préférences de repas, l’assistance et les sélections de bagages seront enregistrées, mais certains services restent soumis à disponibilité.",
    "notifications_offers": "Notifications et offres",
    "notifications_offers_text": "Si vous choisissez de recevoir des mises à jour et promotions, AirGo peut vous contacter par e-mail avec des informations sur votre réservation, des offres et des services.",
    "confirmation_page_title": "Confirmation de réservation",
"booking_confirmed": "Réservation confirmée",
"booking_success_message": "Votre vol a été réservé avec succès",
"booking_reference": "Référence de réservation",
"email_label": "E-mail",
"departure_time_label": "Heure de départ",
"arrival_time_label": "Heure d’arrivée",
"ticket_class_label": "Classe du billet",
"total_paid": "Total payé",
"points_earned": "points gagnés",
"book_another_flight": "Réserver un autre vol",
"manage_my_bookings": "Gérer mes réservations",
"manage_subtitle": "Voir et gérer vos réservations",
"total_points": "Points totaux",
"current_tier": "Niveau actuel",
"points_to": "points pour",
"highest_tier": "Vous êtes déjà au niveau maximum",
"flight_status": "Statut du vol",
"change_status": "Statut de modification",
"latest_request": "Dernière demande",
"update_meal": "Modifier le repas",
"save": "Enregistrer",
"upgrade_cabin": "Améliorer la classe",
"upgrade": "Améliorer",
"no_upgrade": "Aucune amélioration disponible",
"travel_extras": "Extras de voyage",
"extra_baggage": "Bagage supplémentaire",
"priority_boarding": "Embarquement prioritaire",
"wifi": "Wi-Fi",
"request_change": "Demander un changement",
"new_departure": "Nouveau départ",
"new_destination": "Nouvelle destination",
"new_date": "Nouvelle date",
"reason": "Raison",
"submit_request": "Envoyer la demande",
"view_boarding_pass": "Voir la carte d’embarquement",
"cancel_booking": "Annuler la réservation",
"no_bookings": "Vous n’avez aucune réservation",
"available_flights": "Vols disponibles",
"to_connector": "vers",
"on_date": "le",
"from_price": "À partir de",
"seats_left": "places restantes",
"direct_flight": "Vol direct",
"cabin_bag_included": "Bagage cabine inclus",
"seat_selection_available": "Sélection du siège disponible",
"select_flight": "Sélectionner ce vol",
"back_to_search": "Retour à la recherche",
"economy": "Économie",
"premium_economy": "Économie premium",
"business": "Affaires",
"first_class": "Première",
"password": "Mot de passe",
"no_account": "Vous n’avez pas de compte ?",
"create_one": "Créer un compte",
"forgot_password": "Mot de passe oublié ?",
"create_account": "Créer un compte",
"full_name": "Nom complet",
"already_account": "Vous avez déjà un compte ?",
"forgot_password_title": "Mot de passe oublié",
"reset_password": "Réinitialiser le mot de passe",
"account_email": "E-mail du compte",
"new_password": "Nouveau mot de passe",
"confirm_new_password": "Confirmer le nouveau mot de passe",
"update_password": "Mettre à jour le mot de passe",
"back_to_login": "Retour à la connexion",
"boarding_pass": "Carte d’embarquement",
"boarding_gate": "Porte",
"boarding_group": "Groupe",
"not_assigned": "Non attribué",
"print_boarding_pass": "Imprimer la carte",
"no_exact_matches": "Aucune correspondance exacte trouvée. Affichage des vols d’exemple à la place.",
"class_economy": "Économie",
"class_premium": "Économie Premium",
"class_business": "Affaires",
"class_first": "Première",
"any_class": "Toutes",

"benefit_cabin_bag_1": "1 bagage cabine",
"benefit_cabin_bag_checked_1": "1 bagage cabine + 1 bagage en soute",
"benefit_checked_bags_2_cabin_1": "2 bagages en soute + 1 bagage cabine",
"benefit_checked_bags_3_cabin_2": "3 bagages en soute + 2 bagages cabine",

"benefit_standard_meal": "Repas standard",
"benefit_premium_meal": "Repas premium",
"benefit_business_dining": "Restauration en classe affaires",
"benefit_first_dining": "Restauration en première classe",

"benefit_standard_seat_selection": "Sélection standard du siège",
"benefit_included": "Inclus",
"benefit_priority_seat_selection": "Sélection prioritaire du siège",
"benefit_luxury_suite_selection": "Sélection de suite de luxe",

"benefit_not_included": "Non inclus",

"benefit_low_flexibility": "Faible flexibilité",
"benefit_medium_flexibility": "Flexibilité moyenne",
"benefit_high_flexibility": "Grande flexibilité",
"benefit_maximum_flexibility": "Flexibilité maximale",

"price_label": "Prix",
"airline_label": "Compagnie",
"add_another_flight": "Ajouter un autre vol",
"top_choice": "Meilleur choix",
"popular_in_uk": "Populaire au Royaume-Uni",
"long_haul_favourite": "Favori long-courrier",
"flight": "Vol",
"remove_flight": "Supprimer le vol",
"selected_seats": "Sièges sélectionnés",

"search_hotels": "Rechercher des hôtels",
"destination_city": "Ville de destination",
"where_to": "Où allez-vous ?",
"check_in": "Arrivée",
"check_out": "Départ",
"number_of_guests": "Nombre de clients",
"guest": "Client",
"guests": "Clients",
"no_cities_found": "Aucune ville trouvée",
"city_error": "Impossible de charger les villes",
"select_city_alert": "Veuillez sélectionner une ville dans la liste",

"hotel_results_title": "Résultats des hôtels",
"available_hotels_in": "Hôtels disponibles à",
"night": "Nuit",
"nights": "Nuits",
"price_per_night": "Prix par nuit",
"book_hotel": "Réserver l’hôtel",
"no_hotels_found": "Aucun hôtel trouvé pour cette destination.",
"try_another_search": "Essayer une autre recherche",

"location": "Emplacement",
"booking_details": "Détails de la réservation",
"room_type": "Type de chambre",
"total_price": "Prix total",
"booking_payment_message": "En cliquant sur confirmer, votre réservation sera facturée via votre méthode de paiement.",
"confirm_booking": "Confirmer la réservation",
"back_to_results": "Retour aux résultats",

"hotel_booking_confirmed": "Réservation d'hôtel confirmée",
"hotel_success_message": "Votre hôtel a été réservé avec succès",
"booking_reference": "Référence de réservation",
"hotel": "Hôtel",
"total_paid": "Total payé",
"status": "Statut",
"linked_booking": "Cette réservation d'hôtel est liée à votre réservation de vol.",
"view_linked_flight": "Voir la réservation du vol",
"view_all_bookings": "Voir toutes mes réservations",
"back_home": "Retour à l'accueil",

"flight_tracker_title": "Suivi de vol",
"flight_tracker": "Suivi de vol",
"enter_reference": "Entrez votre référence de réservation pour suivre votre vol.",
"example_reference": "ex: ABC12345",
"track_flight": "Suivre le vol",
"no_booking_found": "Aucune réservation trouvée avec cette référence.",
"flight_date": "Date du vol",
"departure": "Départ",
"arrival": "Arrivée",
"back_manage_booking": "Retour à la gestion des réservations",
"airline": "Compagnie aérienne",
"flight_cancelled": "Vol annulé",
"flight_delayed": "Vol retardé — veuillez vérifier plus tard",
"current_status": "Statut actuel",

"no_flights_found": "Aucun vol trouvé",
"no_flights_text": "Nous n'avons trouvé aucun vol correspondant à votre recherche. Essayez de modifier vos critères.",

"hotels": "Hôtels",
"track_flight": "Suivi du vol",

"passengers": "Passagers",
"seat": "Siège",
"refund_status": "Statut du remboursement",
"select_passengers": "Sélectionner les passagers",
"update_meal": "Modifier le repas",
"save_meal": "Enregistrer le repas",
"travel_extras": "Extras de voyage",
"save_extras": "Enregistrer les extras",
"upgrade_cabin": "Surclassement",
"available_upgrades": "Surclassements disponibles",
"upgrade_passenger": "Surclasser ce passager",
"request_refund": "Demander un remboursement",
"reason_refund": "Motif du remboursement",
"flights": "Vols",
"refund_status": "Statut du remboursement",
"refund_amount": "Montant du remboursement",
"requested_refund": "Remboursement demandé",
"passengers_requested": "Passagers demandés",
"remaining_passengers": "Passagers restants",
"request_refund": "Demander un remboursement",
"request_hotel_refund": "Demander un remboursement d’hôtel",
"request_date_change": "Demander un changement de date",
"reason_refund": "Motif du remboursement",
"select_passenger_refund": "Sélectionner le passager à rembourser",
"other_reason": "Autre raison",
"submit_refund_request": "Envoyer la demande de remboursement",
"submit_hotel_refund_request": "Envoyer la demande de remboursement d’hôtel",
"submit_change_request": "Envoyer la demande de changement",
"hotel_bookings": "Réservations d’hôtel",
"hotel_booking": "Réservation d’hôtel",
"hotel": "Hôtel",
"check_in": "Arrivée",
"check_out": "Départ",
"guests": "Clients",
"status": "Statut",
"new_check_in": "Nouvelle arrivée",
"new_check_out": "Nouveau départ",
"requested_dates": "Dates demandées",
"refund_pending": "Demande de remboursement en attente.",
"refund_approved": "Remboursement approuvé.",
"refund_rejected": "Remboursement rejeté.",
"date_change_pending": "Demande de changement en attente.",
"date_change_approved": "Changement de date approuvé.",
"date_change_rejected": "Changement de date rejeté.",
"hotel_cancelled_note": "Les changements de date ne sont pas disponibles car cette réservation d’hôtel est annulée.",
"hotel_refund_pending_note": "Les changements de date ne sont pas disponibles pendant que votre remboursement est en attente.",
"need_hotel": "Besoin d’un hôtel pour ce voyage ?",
"find_hotels_in": "Trouver des hôtels à",
"no_bookings_yet": "Aucune réservation pour le moment",
"no_bookings_text": "Vous n’avez pas encore effectué de réservation. Recherchez un vol pour commencer.",
"change_plans": "Changement de plans",
"found_cheaper_flight": "Vol moins cher trouvé",
"found_cheaper_hotel": "Hôtel moins cher trouvé",
"medical_reason": "Raison médicale",
"visa_passport_issue": "Problème de visa/passeport",
"airline_schedule_issue": "Problème d’horaire de la compagnie",
"travel_disruption": "Perturbation du voyage",
"flight_cancelled_changed": "Vol annulé ou modifié",
"other": "Autre",
"only_fill_other": "Remplissez seulement si vous avez choisi Autre",
"cancelled": "Annulé",
"changed": "Modifié",
"active": "Actif",
"cabin": "Cabine",
"no_checked_bag": "Aucun bagage en soute",
"one_checked_bag": "1 bagage en soute",
"two_checked_bags": "2 bagages en soute",
"lounge_access": "Accès au salon",
"available_upgrades": "Surclassements disponibles",
"upgrade_passenger": "Surclasser ce passager",
"no_upgrades_passenger": "Aucun surclassement disponible pour ce passager.",
"Vegetarian Meal": "Repas végétarien",
"Vegan Meal": "Repas végétalien",
"Halal Meal": "Repas halal",
"Standard Meal": "Repas standard",
"Gluten Free Meal": "Repas sans gluten",
"No Meal": "Aucun repas",
"Economy": "Économie",
"Premium Economy": "Économie premium",
"Business": "Affaires",
"First": "Première",
"Cancelled": "Annulé",
"Approved": "Approuvé",
"Rejected": "Rejeté",
"Pending": "En attente",
"Active": "Actif",
"Changed": "Modifié",
"No checked bag": "Aucun bagage en soute",
"1 checked bag": "1 bagage en soute",
"2 checked bags": "2 bagages en soute",
"Change of plans": "Changement de plans",
"Found cheaper flight": "Vol moins cher trouvé",
"Found cheaper hotel": "Hôtel moins cher trouvé",
"Medical reason": "Raison médicale",
"Visa/passport issue": "Problème de visa/passeport",
"Airline schedule issue": "Problème d’horaire de la compagnie",
"Travel disruption": "Perturbation du voyage",
"Flight cancelled or changed": "Vol annulé ou modifié",
"Other": "Autre",
"CONFIRMED": "CONFIRMÉ",

"Scheduled": "Programmé",
"None": "Aucun",
"one_way": "Aller simple",
"return": "Aller-retour",
"multi_city": "Multi-destinations",
"Passenger": "Passager",
"Passenger 1": "Passager 1",
"Blue": "Bleu",
"Silver": "Argent",
"Gold": "Or",
"Platinum": "Platine",
"Standard": "Standard",
"Deluxe": "Deluxe",
"Suite": "Suite",

"airgo_rewards": "Récompenses AirGo",
"use_points": "Utiliser des points",
"available_points": "Points disponibles",
"discount": "de réduction",
"off": "OFF",
"pay_full_price": "Payer le prix total",

"base_fares": "Tarifs de base",
"seat_selection_price": "Sélection du siège",
"points": "points",
"your_points": "Vos points",
"no_points": "Aucun point",
"secure_checkout": "Paiement sécurisé",
"secure_payment_text": "Paiement sécurisé protégé par AirGo",

"airport_transfers": "Transferts aéroport",
"book_transfer_between": "Réservez un transfert entre un aéroport et votre destination.",
"airport_to_address": "Aéroport → Adresse",
"address_to_airport": "Adresse → Aéroport",
"from_airport": "Depuis — Aéroport",
"to_airport": "Vers — Aéroport",
"destination_address": "Vers — Adresse de destination",
"your_address": "Depuis — Votre adresse",
"address_line_1": "Adresse ligne 1",
"address_line_2": "Adresse ligne 2 (optionnel)",
"town_city": "Ville",
"postcode": "Code postal",
"county": "Comté",
"country": "Pays",
"transfer_type": "Type de transfert",
"search_transfers": "Rechercher des transferts",
"distance": "Distance",
"estimated_travel_time": "Temps de trajet estimé",
"available_transfers": "Transferts disponibles",
"travel_time": "Temps de trajet",
"estimated_price": "Prix estimé",
"book_now": "Réserver",
"search_again": "Rechercher à nouveau",
"loading_map": "Chargement de la carte...",
"map_unavailable": "Carte indisponible dans cet environnement.",
"passenger_details": "Détails du passager",
"confirm_transfer_details": "Confirmez vos informations pour le transfert.",
"first_name": "Prénom",
"last_name": "Nom",
"email_address": "Adresse e-mail",
"mobile_number": "Numéro de téléphone",
"alternative_number": "Numéro alternatif",
"optional": "optionnel",
"special_requests": "Demandes spéciales",
"continue_payment": "Continuer vers le paiement",
"name_on_card": "Nom sur la carte",
"card_number": "Numéro de carte",
"expiry_date": "Date d’expiration",
"complete_booking": "Finaliser la réservation",
"booking_summary": "Résumé de réservation",
"pickup": "Prise en charge",
"dropoff": "Destination",
"total": "Total",
"fare_details": "Détails du tarif",
"use_points": "Utiliser des points",
"your_points": "Vos points",
"points_discount": "Réduction avec points",
"no_points": "Aucun point",
"pay_full_price": "Payer le prix complet",
"booking_confirmed": "Réservation confirmée",
"transfer_booked": "Transfert réservé !",
"transfer_confirmed": "Votre transfert aéroport a été confirmé.",
"booking_reference": "Référence de réservation",
"transfer_details": "Détails du transfert",
"transfer_type_label": "Type de transfert",
"total_paid": "Total payé",
"view_bookings": "Voir mes réservations",
"back_home": "Retour à l’accueil",
"standard_taxi": "Taxi standard",
"up_to_4_passengers": "jusqu’à 4 passagers",

"need_login_transfer": "Vous devez vous connecter avant de pouvoir réserver un transfert.",
"premium": "PREMIUM",
"exclusive": "EXCLUSIF",
"no_transfer_options": "Aucune option de transfert disponible.",
"map_route_unavailable": "Carte indisponible — l’itinéraire n’a pas pu être calculé.",
"standard_taxi_expect": "À quoi s’attendre avec un taxi standard",
"minivan_expect": "À quoi s’attendre avec un minivan",
"luxury_car_expect": "À quoi s’attendre avec une voiture de luxe",
"meet_greet_expect": "À quoi s’attendre avec Accueil personnalisé + transfert de luxe",

"standard_taxi_point_1": "🧳 Vous chargez vous-même vos bagages dans le coffre",
"standard_taxi_point_2": "🚗 Voiture propre et confortable — Toyota Prius ou similaire",
"standard_taxi_point_3": "👤 Jusqu’à 4 passagers",
"standard_taxi_point_4": "📱 Le chauffeur vous contactera à l’arrivée",
"standard_taxi_point_5": "💳 Paiement par carte ou en espèces à la fin du trajet",
"standard_taxi_point_6": "⏱ Le chauffeur attend jusqu’à 15 minutes sans frais supplémentaires",
"standard_taxi_point_7": "🌡 Climatisation incluse",
"standard_taxi_point_8": "🚫 Aucun rafraîchissement fourni",

"minivan_point_1": "👨‍👩‍👧‍👦 Meilleure option pour les groupes de 5 personnes ou plus",
"minivan_point_2": "🚐 Ford Tourneo spacieux ou similaire — jusqu’à 7 places",
"minivan_point_3": "🧳 Grande capacité de bagages",
"minivan_point_4": "🥤 Boisson de bienvenue offerte à tous les passagers",
"minivan_point_5": "🌡 Climatisation complète pendant le trajet",
"minivan_point_6": "🎵 Système de divertissement disponible",
"minivan_point_7": "💺 Sièges larges et confortables avec plus d’espace",
"minivan_point_8": "📱 Le chauffeur vous accueille aux arrivées avec une pancarte",

"luxury_car_point_1": "🚘 Mercedes Classe S ou BMW Série 7 — état impeccable",
"luxury_car_point_2": "👔 Chauffeur professionnel en tenue élégante",
"luxury_car_point_3": "🧳 Le chauffeur s’occupe de tous vos bagages",
"luxury_car_point_4": "🥂 Eau fraîche et confiseries fournies",
"luxury_car_point_5": "📰 Journaux et magazines disponibles sur demande",
"luxury_car_point_6": "🔇 Cabine calme et privée — idéale pour les appels professionnels",
"luxury_car_point_7": "🌡 Climatisation personnalisée",
"luxury_car_point_8": "📱 Le chauffeur vous accueille à l’intérieur du terminal",

"meet_greet_point_1": "✈ Un représentant vous accueille à la porte de l’avion",
"meet_greet_point_2": "🛂 Passage rapide à l’immigration et à la sécurité",
"meet_greet_point_3": "🧳 Un porteur dédié transporte vos bagages",
"meet_greet_point_4": "🚐 Mercedes Classe V à la sortie du terminal — jusqu’à 7 passagers",
"meet_greet_point_5": "🥂 Champagne ou boissons premium à l’arrivée",
"meet_greet_point_6": "📋 Documents de voyage pris en charge pour vous",
"meet_greet_point_7": "🏨 Coordination avec l’hôtel possible sur demande",
"meet_greet_point_8": "📞 Assistance conciergerie 24h/24 et 7j/7",
"transfer_details": "Détails du transfert",
"complete_transfer_booking": "Complétez votre réservation de transfert.",
"full_name": "Nom complet",
"phone_number": "Numéro de téléphone",
"flight_number": "Numéro de vol",
"pickup_date": "Date de prise en charge",
"pickup_time": "Heure de prise en charge",
"luggage": "Bagages",
"special_requests": "Demandes spéciales",
"special_requests_placeholder": "Ajoutez des demandes ou informations importantes...",
"continue_to_payment": "Continuer vers le paiement",
"fare_details": "Détails du tarif",
"transfer_type": "Transfert",
"distance": "Distance",
"travel_time": "Temps de trajet",
"points_discount": "Réduction avec points",
"total": "Total",
"use_points": "Utiliser des points",
"your_points": "Vos points",
"points": "points",
"discount": "de réduction",
"off": "de réduction",
"no_points": "Aucun point",
"pay_full_price": "Payer le prix total",
"booking_summary": "Résumé de réservation",
"passenger_label": "Passager",
"phone_number": "Téléphone",
"alternative_number": "Téléphone alternatif",
"pickup": "Prise en charge",
"dropoff": "Destination",
"name_on_card": "Nom sur la carte",
"card_number": "Numéro de carte",
"expiry_date": "Date d’expiration",
"receive_offers": "Je souhaite recevoir des offres et mises à jour",
"complete_booking": "Finaliser la réservation",
"i_agree_terms": "J’accepte les",
"terms_conditions": "Conditions générales",
"booking_terms": "Conditions de réservation",
"payments": "Paiements",
"changes_cancellations": "Modifications et annulations",
"passenger_responsibility": "Responsabilité du passager",

"booking_terms_text": "En finalisant une réservation avec AirGo, vous confirmez que toutes les informations passagers sont exactes et complètes.",

"payments_text": "Tous les paiements doivent être effectués intégralement avant confirmation de la réservation.",

"changes_cancellations_text": "Les modifications et annulations dépendent du type de transfert et peuvent entraîner des frais supplémentaires.",

"passenger_responsibility_text": "Les passagers doivent être prêts au lieu de prise en charge à l’heure convenue.",
"transfer_booked": "Transfert réservé !",
"transfer_confirmed": "Votre transfert aéroport a été confirmé.",
"view_bookings": "Voir mes réservations",
"taxis": "Taxis",

"hotel_payment": "Paiement hôtel",
"hotel_fare_details": "Détails du tarif hôtel",
"hotel": "Hôtel",
"location": "Emplacement",
"check_in": "Arrivée",
"check_out": "Départ",
"guests": "Invités",
"room_type": "Type de chambre",
"points_discount": "Réduction avec points",
"total": "Total",
"use_points": "Utiliser des points",
"your_points": "Vos points",
"points": "points",
"discount": "de réduction",
"off": "de réduction",
"no_points": "Aucun point",
"pay_full_price": "Payer le prix total",
"name_on_card": "Nom sur la carte",
"card_number": "Numéro de carte",
"expiry_date": "Date d’expiration",
"name_letters_only": "Le nom doit contenir uniquement des lettres",
"card_number_validation": "Le numéro de carte doit contenir exactement 16 chiffres",
"cvv_validation": "Le CVV doit contenir 3 ou 4 chiffres",
"i_agree_terms": "J’accepte les",
"terms_conditions": "Conditions générales",
"receive_offers": "Je souhaite recevoir des offres et mises à jour",
"complete_hotel_booking": "Finaliser la réservation de l’hôtel",
"airport_transfers": "Transferts aéroport",
"date_booked": "Date de réservation",
"price_paid": "Prix payé",
"None": "Confirmé",

"minivan": "Minivan",
"luxury_car": "Voiture de luxe",
"mercedes_s_class": "Mercedes Classe S",
"meet_greet_luxury_transfer": "Accueil VIP + transfert de luxe",

"minute": "min",
"minutes": "min",
<<<<<<< HEAD
"enter_details_for_all": "Entrez les informations pour",
"selected_flights": "Vols sélectionnés",
"choose_seats_for_each_flight_start": "Choisissez",
"for_each_flight": "pour chaque vol.",
"plural_s": "s",
"seats_for": "Sièges pour",
"please_choose_seats_alert": "Veuillez choisir des sièges pour chaque vol avant de continuer. Passagers :",
=======
"need_transfer": "Besoin d’un transfert depuis l’aéroport ?",
"transfer_suggestion_text": "Réservez un taxi ou un transfert de luxe vers votre destination.",
"book_airport_transfer": "Réserver un transfert aéroport",
"need_hotel_in": "Besoin d’un hôtel à",
"hotel_suggestion_text": "Trouvez des hôtels disponibles correspondant à vos dates de voyage à destination.",
"find_hotels_for_trip": "Trouver des hôtels pour ce voyage",
"guest_details": "Détails des voyageurs",
"hotel_guest_details_subtitle": "Entrez les informations de tous les clients séjournant à l’hôtel.",
"guest_special_requests": "Demandes spéciales du client",
"guest_special_requests_placeholder": "Ajoutez des demandes pour ce client...",
"continue_to_hotel_payment": "Continuer vers le paiement de l’hôtel",
"continue_guest_details": "Continuer vers les détails des voyageurs",
"selected_flights": "Vols Sélectionnés",
"seats_for": "Places Pour",
"per_passenger": "Par Passager",
<<<<<<< HEAD
"scheduled": "Prévue",
"boarding": "Embarquement",
"departed": "Décollé",
"landed": "Atterri",
"total_stay_price": "Prix total du séjour",
=======
>>>>>>> 4b446d46dc475c3831deb317bcd77dae800f209c
>>>>>>> b7aa1d88ca5ad71568b2755e0c90c1c795c2d72e
},

    "ar": {
    "welcome": "مرحبًا بك في AirGo",
    "subtitle": "احجز وأدر رحلاتك مباشرة مع شركتنا",
    "search": "ابحث عن رحلات",
    "manage_booking": "إدارة الحجز",
    "admin": "الإدارة",
    "logout": "تسجيل الخروج",
    "login": "تسجيل الدخول",
    "signup": "إنشاء حساب",
    "search_currency": "ابحث عن عملة...",

    "trip_type": "نوع الرحلة",
    "from_label": "من",
    "to_label": "إلى",
    "departure_date": "تاريخ المغادرة",
    "return_date": "تاريخ العودة",
    "second_flight": "الرحلة الثانية",
    "passengers": "المسافرون",
    "class_label": "الدرجة",
    "example_departure":" مطار المغادرة",
    "example_arrival": "مطار الوصول",

    "return_trip": "ذهاب وعودة",
    "one_way": "ذهاب فقط",
    "multi_city": "مدن متعددة",

    "popular_routes": "الوجهات الشائعة",
    "explore_destinations": "اكتشف الوجهات الأكثر حجزًا",
    "choose_destination": "اختر وجهة لملء البحث بسرعة.",
    "uk": "المملكة المتحدة",
    "usa": "الولايات المتحدة",
    "tr": "تركيا",
    "lba": "ليدز",
    "jfk": "نيو يورك",
    "ist": "اسطنبول",

    "passenger_details_title": "تفاصيل المسافر",
    "selected_flight": "الرحلة المحددة",
    "whats_included": "ما هو المشمول مع",
    "first_name": "الاسم الأول",
    "last_name": "اسم العائلة",
    "email_address": "البريد الإلكتروني",
    "phone_number": "رقم الهاتف",
    "passport_number": "رقم جواز السفر",

    "baggage": "الأمتعة",
    "meal": "الوجبة",
    "seat_selection": "اختيار المقعد",
    "lounge": "الصالة",
    "flexibility": "المرونة",

    "assistance_title": "إمكانية الوصول والمساعدة الخاصة",
    "assistance_text": "يتم تقديم هذه الخدمة دون تكلفة إضافية. أخبرنا إذا كنت بحاجة إلى أي دعم أثناء رحلتك.",
    "assistance_required": "أحتاج إلى مساعدة خاصة",
    "other_assistance": "احتياجات مساعدة أخرى",
    "other_assistance_placeholder": "يرجى وصف أي دعم آخر قد تحتاجه",

    "wheelchair_assistance": "مساعدة الكرسي المتحرك",
    "visual_assistance": "مساعدة بصرية",
    "hearing_assistance": "مساعدة سمعية",
    "pregnancy_support": "دعم الحمل",
    "travelling_with_infant": "السفر مع رضيع",
    "elderly_support": "دعم المسافر المسن",
    "medical_assistance": "مساعدة طبية",
    "extra_boarding_time": "وقت إضافي للصعود",
    "airport_security_assistance": "مساعدة المطار/الأمن",
    "special_seating_request": "طلب مقعد خاص",

    "extras_title": "اختر الإضافات",
    "extras_subtitle": "اختر أي إضافات لرحلتك قبل المتابعة.",
    "your_flight": "رحلتك",
    "airline": "شركة الطيران",
    "route": "المسار",
    "base_price": "السعر الأساسي",
    "baggage_options": "خيارات الأمتعة",
    "checked_baggage": "الأمتعة المسجلة",
    "no_checked_bag": "بدون أمتعة مسجلة",
    "one_checked_bag": "حقيبة مسجلة واحدة",
    "two_checked_bags": "حقيبتان مسجلتان",
    "meal_preference": "تفضيل الوجبة",
    "choose_your_meal": "اختر وجبتك",
    "standard_meal": "وجبة عادية",
    "halal_meal": "وجبة حلال",
    "vegetarian_meal": "وجبة نباتية",
    "vegan_meal": "وجبة نباتية صِرفة",
    "gluten_free_meal": "وجبة خالية من الغلوتين",
    "no_meal": "بدون وجبة",
    "travel_insurance": "تأمين السفر",
    "insurance_text": "احمِ رحلتك بتغطية اختيارية قبل الدفع.",
    "recommended": "موصى به",
    "travel_protection": "حماية السفر من AirGo",
    "only_per_booking": "فقط",
    "per_booking": "لكل حجز",
    "insurance_benefit_1": "تغيير الرحلة حتى 24 ساعة قبل المغادرة",
    "insurance_benefit_2": "الدعم أثناء التأخير وتعطل السفر",
    "insurance_benefit_3": "مساعدة طارئة أثناء السفر عند الحاجة",
    "insurance_benefit_4": "مرونة إضافية وراحة بال",
    "add_travel_insurance": "إضافة تأمين السفر",
    "continue_without_insurance": "لا، المتابعة بدون تأمين",
    "continue_to_seat_selection": "المتابعة إلى اختيار المقعد",

    "seat_selection_title": "اختيار المقعد",
    "choose_seat": "اختر مقعدك",
    "choose_seat_subtitle": "اختر منطقة المقصورة والمقعد المفضل.",
    "seat_prices": "أسعار المقاعد",
    "window_seat": "مقعد بجانب النافذة",
    "aisle_seat": "مقعد بجانب الممر",
    "middle_seat": "مقعد وسط",
    "exit_seat": "مقعد مخرج الطوارئ",
    "extra_legroom": "مساحة إضافية للأرجل",
    "no_selection": "بدون اختيار",
    "random_seat": "يتم تعيين المقعد عشوائيًا",
    "available": "متاح",
    "unavailable": "غير متاح",
    "selected": "محدد",
    "selected_seat": "المقعد المحدد",
    "seat_type": "نوع المقعد",
    "seat_price": "سعر المقعد",
    "continue_review": "المتابعة إلى المراجعة",
    "none": "لا يوجد",
    "time": "الوقت",
    "fare": "السعر",

    "continue_to_extras": "المتابعة إلى الإضافات",
    "review_title": "مراجعة الحجز",
    "review_subtitle": "يرجى مراجعة الرحلة وبيانات المسافر والإضافات قبل المتابعة للدفع.",
    "flight_details": "تفاصيل الرحلة",
    "date": "التاريخ",
    "departure": "المغادرة",
    "arrival": "الوصول",
    "back_manage_booking": "العودة إلى إدارة الحجز",
    "seat": "المقعد",
    "selected_extras": "الإضافات المختارة",
    "name": "الاسم",
    "no_baggage": "لا توجد أمتعة إضافية",
    "no_insurance": "لا يوجد تأمين سفر",
    "back": "رجوع",
    "continue_payment": "المتابعة إلى الدفع",

    "payment_title": "الدفع",
    "fare_details": "تفاصيل السعر",
    "includes_taxes": "يشمل الضرائب والرسوم",
    "total": "الإجمالي",
    "booking_summary": "ملخص الحجز",
    "passenger_label": "المسافر",
    "flight_label": "الرحلة",
    "name_on_card": "الاسم على البطاقة",
    "card_number": "رقم البطاقة",
    "expiry_date": "تاريخ الانتهاء",
    "expiry_placeholder": "شهر/سنة",
    "cvv": "رمز التحقق",
    "agree_terms_1": "أوافق على",
    "terms_conditions": "الشروط والأحكام",
    "receive_offers": "أرغب في تلقي العروض والتحديثات",
    "complete_booking": "إكمال الحجز",
    "booking_terms": "شروط الحجز",
    "booking_terms_text": "من خلال إكمال الحجز مع AirGo، فإنك تؤكد أن جميع بيانات المسافر المقدمة صحيحة وكاملة.",
    "payments": "المدفوعات",
    "payments_text": "يجب إتمام جميع المدفوعات بالكامل قبل تأكيد الحجز. الأسعار المعروضة عند الدفع تشمل الرحلة المختارة والإضافات المحددة.",
    "changes_cancellations": "التغييرات والإلغاءات",
    "changes_cancellations_text": "تخضع التغييرات والإلغاءات لنوع السعر وسياسة شركة الطيران. قد يتم تطبيق رسوم إضافية حسب الطلب.",
    "passenger_responsibility": "مسؤولية المسافر",
    "passenger_responsibility_text": "المسافرون مسؤولون عن التأكد من امتلاكهم لوثائق سفر صالحة، بما في ذلك جوازات السفر والتأشيرات وأي هوية مطلوبة.",
    "special_requests": "الطلبات الخاصة",
    "special_requests_text": "سيتم تسجيل الطلبات مثل تفضيلات الوجبات والمساعدة واختيارات الأمتعة، ولكن بعض الخدمات تبقى رهن التوفر.",
    "notifications_offers": "الإشعارات والعروض",
    "notifications_offers_text": "إذا اخترت تلقي التحديثات والعروض، فقد تتواصل AirGo معك عبر البريد الإلكتروني بشأن تحديثات الحجز والعروض ومعلومات الخدمة.",
    "confirmation_page_title": "تأكيد الحجز",
"booking_confirmed": "تم تأكيد الحجز",
"booking_success_message": "تم حجز رحلتك بنجاح",
"booking_reference": "مرجع الحجز",
"email_label": "البريد الإلكتروني",
"departure_time_label": "وقت المغادرة",
"arrival_time_label": "وقت الوصول",
"ticket_class_label": "درجة التذكرة",
"total_paid": "إجمالي المبلغ المدفوع",
"points_earned": "نقطة مكتسبة",
"book_another_flight": "احجز رحلة أخرى",
"manage_my_bookings": "إدارة حجوزاتي",
"manage_subtitle": "عرض وإدارة حجوزاتك",
"total_points": "إجمالي النقاط",
"current_tier": "المستوى الحالي",
"points_to": "نقطة للوصول إلى",
"highest_tier": "أنت بالفعل في أعلى مستوى",
"flight_status": "حالة الرحلة",
"change_status": "حالة التغيير",
"latest_request": "آخر طلب",
"update_meal": "تحديث الوجبة",
"save": "حفظ",
"upgrade_cabin": "ترقية الدرجة",
"upgrade": "ترقية",
"no_upgrade": "لا توجد ترقيات متاحة",
"travel_extras": "إضافات السفر",
"extra_baggage": "أمتعة إضافية",
"priority_boarding": "صعود أولوية",
"wifi": "واي فاي",
"request_change": "طلب تغيير",
"new_departure": "مغادرة جديدة",
"new_destination": "وجهة جديدة",
"new_date": "تاريخ جديد",
"reason": "السبب",
"submit_request": "إرسال الطلب",
"view_boarding_pass": "عرض بطاقة الصعود",
"cancel_booking": "إلغاء الحجز",
"no_bookings": "لا توجد حجوزات",
"available_flights": "الرحلات المتاحة",
"to_connector": "إلى",
"on_date": "في",
"from_price": "ابتداءً من",
"seats_left": "مقعدًا متبقيًا",
"direct_flight": "رحلة مباشرة",
"cabin_bag_included": "حقيبة مقصورة مشمولة",
"seat_selection_available": "اختيار المقعد متاح",
"select_flight": "اختر هذه الرحلة",
"back_to_search": "العودة إلى البحث",
"economy": "اقتصادية",
"premium_economy": "اقتصادية مميزة",
"business": "رجال الأعمال",
"first_class": "الأولى",
"password": "كلمة المرور",
"no_account": "ليس لديك حساب؟",
"create_one": "أنشئ حسابًا",
"forgot_password": "هل نسيت كلمة المرور؟",
"create_account": "إنشاء حساب",
"full_name": "الاسم الكامل",
"already_account": "هل لديك حساب بالفعل؟",
"forgot_password_title": "نسيت كلمة المرور",
"reset_password": "إعادة تعيين كلمة المرور",
"account_email": "بريد الحساب الإلكتروني",
"new_password": "كلمة المرور الجديدة",
"confirm_new_password": "تأكيد كلمة المرور الجديدة",
"update_password": "تحديث كلمة المرور",
"back_to_login": "العودة إلى تسجيل الدخول",
"boarding_pass": "بطاقة الصعود",
"boarding_gate": "البوابة",
"boarding_group": "المجموعة",
"not_assigned": "غير محدد",
"print_boarding_pass": "طباعة بطاقة الصعود",
"no_exact_matches": "لم يتم العثور على نتائج مطابقة تمامًا. يتم عرض رحلات تجريبية بدلًا من ذلك.",
"class_economy": "اقتصادية",
"class_premium": "اقتصادية مميزة",
"class_business": "رجال الأعمال",
"class_first": "الأولى",
"any_class": "الكل",

"benefit_cabin_bag_1": "حقيبة مقصورة واحدة",
"benefit_cabin_bag_checked_1": "حقيبة مقصورة واحدة + حقيبة مسجلة واحدة",
"benefit_checked_bags_2_cabin_1": "حقيبتان مسجلتان + حقيبة مقصورة واحدة",
"benefit_checked_bags_3_cabin_2": "3 حقائب مسجلة + حقيبتا مقصورة",

"benefit_standard_meal": "وجبة عادية",
"benefit_premium_meal": "وجبة مميزة",
"benefit_business_dining": "وجبات درجة رجال الأعمال",
"benefit_first_dining": "وجبات الدرجة الأولى",

"benefit_standard_seat_selection": "اختيار مقعد عادي",
"benefit_included": "مشمول",
"benefit_priority_seat_selection": "اختيار مقعد بأولوية",
"benefit_luxury_suite_selection": "اختيار جناح فاخر",

"benefit_not_included": "غير مشمول",

"benefit_low_flexibility": "مرونة منخفضة",
"benefit_medium_flexibility": "مرونة متوسطة",
"benefit_high_flexibility": "مرونة عالية",
"benefit_maximum_flexibility": "أقصى مرونة",

"price_label": "السعر",
"airline_label": "شركة الطيران",
"add_another_flight": "إضافة رحلة أخرى",
"top_choice": "الخيار الأفضل",
"popular_in_uk": "شائع في المملكة المتحدة",
"long_haul_favourite": "مفضل للرحلات الطويلة",
"flight": "رحلة",
"remove_flight": "إزالة الرحلة",
"selected_seats": "المقاعد المحددة",

"search_hotels": "البحث عن فنادق",
"destination_city": "مدينة الوجهة",
"where_to": "إلى أين؟",
"check_in": "تسجيل الوصول",
"check_out": "تسجيل المغادرة",
"number_of_guests": "عدد الضيوف",
"guest": "ضيف",
"guests": "ضيوف",
"no_cities_found": "لم يتم العثور على مدن",
"city_error": "تعذر تحميل المدن",
"select_city_alert": "يرجى اختيار مدينة من القائمة",

"hotel_results_title": "نتائج الفنادق",
"available_hotels_in": "الفنادق المتاحة في",
"night": "ليلة",
"nights": "ليالٍ",
"price_per_night": "السعر لكل ليلة",
"book_hotel": "حجز الفندق",
"no_hotels_found": "لم يتم العثور على فنادق لهذه الوجهة.",
"try_another_search": "جرّب بحثًا آخر",

"location": "الموقع",
"booking_details": "تفاصيل الحجز",
"room_type": "نوع الغرفة",
"total_price": "السعر الإجمالي",
"booking_payment_message": "بالنقر على تأكيد، سيتم خصم المبلغ باستخدام طريقة الدفع الخاصة بك.",
"confirm_booking": "تأكيد الحجز",
"back_to_results": "العودة إلى النتائج",

"hotel_booking_confirmed": "تم تأكيد حجز الفندق",
"hotel_success_message": "تم حجز الفندق بنجاح",
"booking_reference": "رقم الحجز",
"hotel": "الفندق",
"total_paid": "المبلغ المدفوع",
"status": "الحالة",
"linked_booking": "هذا الحجز مرتبط بحجز رحلتك الجوية.",
"view_linked_flight": "عرض حجز الرحلة",
"view_all_bookings": "عرض جميع حجوزاتي",
"back_home": "العودة إلى الصفحة الرئيسية",

"flight_tracker_title": "تتبع الرحلة",
"flight_tracker": "تتبع الرحلة",
"enter_reference": "أدخل رقم الحجز لتتبع حالة الرحلة.",
"example_reference": "مثال: ABC12345",
"track_flight": "تتبع الرحلة",
"no_booking_found": "لم يتم العثور على حجز بهذا الرقم.",
"flight_date": "تاريخ الرحلة",
"departure": "المغادرة",
"arrival": "الوصول",
"airline": "شركة الطيران",
"flight_cancelled": "تم إلغاء الرحلة",
"flight_delayed": "الرحلة متأخرة — تحقق لاحقًا",
"current_status": "الحالة الحالية",

"no_flights_found": "لم يتم العثور على رحلات",
"no_flights_text": "لم نجد أي رحلات تطابق بحثك. حاول تعديل معايير البحث.",

"hotels": "الفنادق",
"track_flight": "تتبع الرحلة",

"passengers": "المسافرون",
"seat": "المقعد",
"refund_status": "حالة الاسترداد",
"select_passengers": "اختر المسافرين",
"update_meal": "تعديل الوجبة",
"save_meal": "حفظ الوجبة",
"travel_extras": "إضافات السفر",
"save_extras": "حفظ الإضافات",
"upgrade_cabin": "ترقية الدرجة",
"available_upgrades": "الترقيات المتاحة",
"upgrade_passenger": "ترقية هذا المسافر",
"request_refund": "طلب استرداد",
"reason_refund": "سبب الاسترداد",
"flights": "الرحلات",
"refund_status": "حالة الاسترداد",
"refund_amount": "مبلغ الاسترداد",
"requested_refund": "الاسترداد المطلوب",
"passengers_requested": "المسافرون المطلوبون",
"remaining_passengers": "المسافرون المتبقون",
"request_refund": "طلب استرداد",
"request_hotel_refund": "طلب استرداد الفندق",
"request_date_change": "طلب تغيير التاريخ",
"reason_refund": "سبب الاسترداد",
"select_passenger_refund": "اختر المسافر للاسترداد",
"other_reason": "سبب آخر",
"submit_refund_request": "إرسال طلب الاسترداد",
"submit_hotel_refund_request": "إرسال طلب استرداد الفندق",
"submit_change_request": "إرسال طلب التغيير",
"hotel_bookings": "حجوزات الفنادق",
"hotel_booking": "حجز الفندق",
"hotel": "الفندق",
"check_in": "تسجيل الوصول",
"check_out": "تسجيل المغادرة",
"guests": "الضيوف",
"status": "الحالة",
"new_check_in": "تاريخ وصول جديد",
"new_check_out": "تاريخ مغادرة جديد",
"requested_dates": "التواريخ المطلوبة",
"refund_pending": "طلب الاسترداد قيد الانتظار.",
"refund_approved": "تمت الموافقة على الاسترداد.",
"refund_rejected": "تم رفض الاسترداد.",
"date_change_pending": "طلب التغيير قيد الانتظار.",
"date_change_approved": "تمت الموافقة على تغيير التاريخ.",
"date_change_rejected": "تم رفض تغيير التاريخ.",
"hotel_cancelled_note": "تغيير التاريخ غير متاح لأن حجز الفندق ملغى.",
"hotel_refund_pending_note": "تغيير التاريخ غير متاح أثناء انتظار طلب الاسترداد.",
"need_hotel": "هل تحتاج إلى فندق لهذه الرحلة؟",
"find_hotels_in": "ابحث عن فنادق في",
"no_bookings_yet": "لا توجد حجوزات بعد",
"no_bookings_text": "لم تقم بأي حجز بعد. ابحث عن رحلة لبدء الحجز.",
"change_plans": "تغيير الخطط",
"found_cheaper_flight": "تم العثور على رحلة أرخص",
"found_cheaper_hotel": "تم العثور على فندق أرخص",
"medical_reason": "سبب طبي",
"visa_passport_issue": "مشكلة في التأشيرة أو جواز السفر",
"airline_schedule_issue": "مشكلة في جدول شركة الطيران",
"travel_disruption": "اضطراب في السفر",
"flight_cancelled_changed": "تم إلغاء الرحلة أو تغييرها",
"other": "أخرى",
"only_fill_other": "املأ هذا فقط إذا اخترت أخرى",
"cancelled": "ملغى",
"changed": "تم التغيير",
"active": "نشط",
"cabin": "الدرجة",
"no_checked_bag": "بدون أمتعة مسجلة",
"one_checked_bag": "حقيبة مسجلة واحدة",
"two_checked_bags": "حقيبتان مسجلتان",
"lounge_access": "دخول الصالة",
"available_upgrades": "الترقيات المتاحة",
"upgrade_passenger": "ترقية هذا المسافر",
"no_upgrades_passenger": "لا توجد ترقيات متاحة لهذا المسافر.",
"Vegetarian Meal": "وجبة نباتية",
"Vegan Meal": "وجبة نباتية صِرفة",
"Halal Meal": "وجبة حلال",
"Standard Meal": "وجبة عادية",
"Gluten Free Meal": "وجبة خالية من الغلوتين",
"No Meal": "بدون وجبة",
"Economy": "اقتصادية",
"Premium Economy": "اقتصادية مميزة",
"Business": "رجال الأعمال",
"First": "الأولى",
"Cancelled": "ملغى",
"Approved": "تمت الموافقة",
"Rejected": "مرفوض",
"Pending": "قيد الانتظار",
"Active": "نشط",
"Changed": "تم التغيير",
"No checked bag": "بدون أمتعة مسجلة",
"1 checked bag": "حقيبة مسجلة واحدة",
"2 checked bags": "حقيبتان مسجلتان",
"Change of plans": "تغيير الخطط",
"Found cheaper flight": "تم العثور على رحلة أرخص",
"Found cheaper hotel": "تم العثور على فندق أرخص",
"Medical reason": "سبب طبي",
"Visa/passport issue": "مشكلة في التأشيرة أو جواز السفر",
"Airline schedule issue": "مشكلة في جدول شركة الطيران",
"Travel disruption": "اضطراب في السفر",
"Flight cancelled or changed": "تم إلغاء الرحلة أو تغييرها",
"Other": "أخرى",
"CONFIRMED": "مؤكد",

"Scheduled": "مجدولة",
"None": "لا يوجد",
"one_way": "ذهاب فقط",
"return": "ذهاب وعودة",
"multi_city": "مدن متعددة",
"Passenger": "المسافر",
"Passenger 1": "المسافر 1",
"Blue": "الأزرق",
"Silver": "الفضي",
"Gold": "الذهبي",
"Platinum": "البلاتيني",
"Standard": "عادية",
"Deluxe": "فاخرة",
"Suite": "جناح",

"airgo_rewards": "مكافآت AirGo",
"use_points": "استخدام النقاط",
"available_points": "النقاط المتاحة",
"discount": "خصم",
"off": "خصم",
"pay_full_price": "دفع السعر الكامل",

"base_fares": "الأسعار الأساسية",
"seat_selection_price": "اختيار المقعد",
"points": "نقاط",
"your_points": "نقاطك",
"no_points": "بدون نقاط",
"secure_checkout": "دفع آمن",
"secure_payment_text": "دفع آمن ومحمي من AirGo",

"airport_transfers": "خدمات النقل من المطار",
"book_transfer_between": "احجز خدمة نقل بين المطار ووجهتك.",
"airport_to_address": "المطار ← العنوان",
"address_to_airport": "العنوان ← المطار",
"from_airport": "من — المطار",
"to_airport": "إلى — المطار",
"destination_address": "إلى — عنوان الوجهة",
"your_address": "من — عنوانك",
"address_line_1": "العنوان 1",
"address_line_2": "العنوان 2 (اختياري)",
"town_city": "المدينة",
"postcode": "الرمز البريدي",
"county": "المقاطعة",
"country": "الدولة",
"transfer_type": "نوع النقل",
"search_transfers": "البحث عن وسائل النقل",
"distance": "المسافة",
"estimated_travel_time": "مدة الرحلة المتوقعة",
"available_transfers": "وسائل النقل المتاحة",
"travel_time": "مدة الرحلة",
"estimated_price": "السعر المتوقع",
"book_now": "احجز الآن",
"search_again": "البحث مرة أخرى",
"loading_map": "جارٍ تحميل الخريطة...",
"map_unavailable": "الخريطة غير متوفرة في هذه البيئة.",
"passenger_details": "تفاصيل المسافر",
"confirm_transfer_details": "أكد معلوماتك الخاصة بالحجز.",
"first_name": "الاسم الأول",
"last_name": "اسم العائلة",
"email_address": "البريد الإلكتروني",
"mobile_number": "رقم الهاتف",
"alternative_number": "رقم بديل",
"optional": "اختياري",
"special_requests": "طلبات خاصة",
"continue_payment": "المتابعة إلى الدفع",
"name_on_card": "الاسم على البطاقة",
"card_number": "رقم البطاقة",
"expiry_date": "تاريخ الانتهاء",
"complete_booking": "إتمام الحجز",
"booking_summary": "ملخص الحجز",
"pickup": "مكان الاستلام",
"dropoff": "الوجهة",
"total": "الإجمالي",
"fare_details": "تفاصيل السعر",
"use_points": "استخدام النقاط",
"your_points": "نقاطك",
"points_discount": "خصم النقاط",
"no_points": "بدون نقاط",
"pay_full_price": "دفع السعر الكامل",
"booking_confirmed": "تم تأكيد الحجز",
"transfer_booked": "تم حجز النقل!",
"transfer_confirmed": "تم تأكيد خدمة النقل الخاصة بك.",
"booking_reference": "رقم الحجز",
"transfer_details": "تفاصيل النقل",
"transfer_type_label": "نوع النقل",
"total_paid": "المبلغ المدفوع",
"view_bookings": "عرض حجوزاتي",
"back_home": "العودة للرئيسية",
"standard_taxi": "تاكسي عادي",
"up_to_4_passengers": "حتى 4 ركاب",

"need_login_transfer": "يجب تسجيل الدخول قبل حجز خدمة النقل.",
"premium": "مميز",
"exclusive": "حصري",
"no_transfer_options": "لا توجد خيارات نقل متاحة.",
"map_route_unavailable": "الخريطة غير متاحة — تعذر حساب المسار.",
"standard_taxi_expect": "ما الذي تتوقعه مع التاكسي العادي",
"minivan_expect": "ما الذي تتوقعه مع الميني فان",
"luxury_car_expect": "ما الذي تتوقعه مع السيارة الفاخرة",
"meet_greet_expect": "ما الذي تتوقعه مع خدمة الاستقبال والنقل الفاخر",

"standard_taxi_point_1": "🧳 تقوم بتحميل أمتعتك بنفسك في صندوق السيارة",
"standard_taxi_point_2": "🚗 سيارة نظيفة ومريحة — تويوتا بريوس أو ما شابه",
"standard_taxi_point_3": "👤 حتى 4 ركاب",
"standard_taxi_point_4": "📱 سيتواصل معك السائق عند الوصول",
"standard_taxi_point_5": "💳 الدفع بالبطاقة أو نقدًا في نهاية الرحلة",
"standard_taxi_point_6": "⏱ ينتظر السائق حتى 15 دقيقة بدون رسوم إضافية",
"standard_taxi_point_7": "🌡 تكييف هواء مشمول",
"standard_taxi_point_8": "🚫 لا توجد مرطبات مقدمة",

"minivan_point_1": "👨‍👩‍👧‍👦 الخيار الأفضل للمجموعات من 5 أشخاص أو أكثر",
"minivan_point_2": "🚐 فورد تورنيو واسعة أو ما شابه — حتى 7 ركاب",
"minivan_point_3": "🧳 مساحة كبيرة للأمتعة",
"minivan_point_4": "🥤 مشروب ترحيبي مجاني لجميع الركاب",
"minivan_point_5": "🌡 تحكم كامل بالمناخ طوال الرحلة",
"minivan_point_6": "🎵 نظام ترفيه داخل السيارة متاح",
"minivan_point_7": "💺 مقاعد واسعة ومريحة مع مساحة إضافية",
"minivan_point_8": "📱 يستقبلك السائق في صالة الوصول بلوحة اسم",

"luxury_car_point_1": "🚘 مرسيدس S-Class أو BMW الفئة السابعة — بحالة ممتازة",
"luxury_car_point_2": "👔 سائق محترف بلباس رسمي",
"luxury_car_point_3": "🧳 السائق يتولى حمل جميع أمتعتك",
"luxury_car_point_4": "🥂 مياه باردة وحلوى مقدمة",
"luxury_car_point_5": "📰 صحف ومجلات متاحة عند الطلب",
"luxury_car_point_6": "🔇 مقصورة هادئة وخاصة — مثالية للمكالمات العملية",
"luxury_car_point_7": "🌡 تحكم شخصي بدرجة الحرارة",
"luxury_car_point_8": "📱 يستقبلك السائق داخل مبنى المطار",

"meet_greet_point_1": "✈ يستقبلك ممثل عند بوابة الطائرة مباشرة",
"meet_greet_point_2": "🛂 مرور سريع عبر الجوازات والأمن",
"meet_greet_point_3": "🧳 حامل أمتعة مخصص يتولى حقائبك",
"meet_greet_point_4": "🚐 مرسيدس V-Class بانتظارك عند مخرج المطار — حتى 7 ركاب",
"meet_greet_point_5": "🥂 شامبانيا أو مشروبات فاخرة عند الوصول",
"meet_greet_point_6": "📋 يتم التعامل مع وثائق السفر نيابة عنك",
"meet_greet_point_7": "🏨 يمكن تنسيق تسجيل الدخول في الفندق عند الطلب",
"meet_greet_point_8": "📞 دعم كونسيرج على مدار الساعة",
"transfer_details": "تفاصيل النقل",
"complete_transfer_booking": "أكمل حجز خدمة النقل الخاصة بك.",
"full_name": "الاسم الكامل",
"phone_number": "رقم الهاتف",
"flight_number": "رقم الرحلة",
"pickup_date": "تاريخ الاستلام",
"pickup_time": "وقت الاستلام",
"luggage": "الأمتعة",
"special_requests": "طلبات خاصة",
"special_requests_placeholder": "أضف أي طلبات أو معلومات مهمة...",
"continue_to_payment": "المتابعة إلى الدفع",
"fare_details": "تفاصيل السعر",
"transfer_type": "النقل",
"distance": "المسافة",
"travel_time": "مدة الرحلة",
"points_discount": "خصم النقاط",
"total": "الإجمالي",
"use_points": "استخدام النقاط",
"your_points": "نقاطك",
"points": "نقاط",
"discount": "خصم",
"off": "خصم",
"no_points": "بدون نقاط",
"pay_full_price": "دفع السعر الكامل",
"booking_summary": "ملخص الحجز",
"passenger_label": "المسافر",
"phone_number": "الهاتف",
"alternative_number": "هاتف بديل",
"pickup": "مكان الاستلام",
"dropoff": "الوجهة",
"name_on_card": "الاسم على البطاقة",
"card_number": "رقم البطاقة",
"expiry_date": "تاريخ الانتهاء",
"receive_offers": "أرغب في تلقي العروض والتحديثات",
"complete_booking": "إتمام الحجز",
"i_agree_terms": "أوافق على",
"terms_conditions": "الشروط والأحكام",
"booking_terms": "شروط الحجز",
"payments": "المدفوعات",
"changes_cancellations": "التعديلات والإلغاءات",
"passenger_responsibility": "مسؤولية المسافر",

"booking_terms_text": "بإتمام الحجز مع AirGo فإنك تؤكد أن جميع بيانات المسافرين صحيحة وكاملة.",

"payments_text": "يجب إتمام جميع المدفوعات بالكامل قبل تأكيد الحجز.",

"changes_cancellations_text": "تخضع التعديلات والإلغاءات لنوع خدمة النقل وقد تترتب عليها رسوم إضافية.",

"passenger_responsibility_text": "يتحمل المسافرون مسؤولية التواجد في موقع الاستلام في الوقت المحدد.",
"transfer_booked": "تم حجز النقل!",
"transfer_confirmed": "تم تأكيد خدمة النقل من المطار.",
"view_bookings": "عرض حجوزاتي",
"taxis": "سيارات الأجرة",

"hotel_payment": "دفع الفندق",
"hotel_fare_details": "تفاصيل سعر الفندق",
"hotel": "الفندق",
"location": "الموقع",
"check_in": "تسجيل الوصول",
"check_out": "تسجيل المغادرة",
"guests": "الضيوف",
"room_type": "نوع الغرفة",
"points_discount": "خصم النقاط",
"total": "الإجمالي",
"use_points": "استخدام النقاط",
"your_points": "نقاطك",
"points": "نقاط",
"discount": "خصم",
"off": "خصم",
"no_points": "بدون نقاط",
"pay_full_price": "دفع السعر الكامل",
"name_on_card": "الاسم على البطاقة",
"card_number": "رقم البطاقة",
"expiry_date": "تاريخ الانتهاء",
"name_letters_only": "يجب أن يحتوي الاسم على أحرف فقط",
"card_number_validation": "يجب أن يتكون رقم البطاقة من 16 رقمًا بالضبط",
"cvv_validation": "يجب أن يتكون CVV من 3 أو 4 أرقام",
"i_agree_terms": "أوافق على",
"terms_conditions": "الشروط والأحكام",
"receive_offers": "أرغب في تلقي العروض والتحديثات",
"complete_hotel_booking": "إتمام حجز الفندق",
"airport_transfers": "خدمات النقل من المطار",
"date_booked": "تاريخ الحجز",
"price_paid": "السعر المدفوع",
"None": "مؤكد",

"minivan": "ميني فان",
"luxury_car": "سيارة فاخرة",
"mercedes_s_class": "مرسيدس S-Class",
"meet_greet_luxury_transfer": "استقبال VIP + نقل فاخر",

"minute": "min",
"minutes": "min",
<<<<<<< HEAD
"enter_details_for_all": "أدخل التفاصيل لجميع",
"selected_flights": "الرحلات المختارة",
"choose_seats_for_each_flight_start": "اختر",
"for_each_flight": "لكل رحلة.",
"plural_s": "",
"seats_for": "المقاعد للرحلة",
"please_choose_seats_alert": "يرجى اختيار المقاعد لكل رحلة قبل المتابعة. عدد المسافرين:",

=======
"need_transfer": "تحتاج نقل من المطار؟",
"transfer_suggestion_text": "احجز تاكسي أو نقل فاخر لوجهتك.",
"book_airport_transfer": "احجز نقل من المطار",
"need_hotel_in": "تحتاج فندق في",
"hotel_suggestion_text": "لقّى فنادق متوفرة توافق تواريخ سفرك في وجهتك.",
"find_hotels_for_trip": "لقّى فنادق لهذا السفر",
"guest_details": "تفاصيل الضيوف",
"hotel_guest_details_subtitle": "دخل معلومات جميع الضيوف اللي راهم حابين يقيمو في الفندق.",
"guest_special_requests": "طلبات خاصة للضيف",
"guest_special_requests_placeholder": "زيد أي طلبات خاصة لهذا الضيف...",
"continue_to_hotel_payment": "واصل للدفع تاع الفندق",
"continue_guest_details": "واصل لتفاصيل الضيوف",
"selected_flights": "الرحلات المختارة",
"seats_for": "مقاعد لـ",
"per_passenger": "لكل مسافر",
<<<<<<< HEAD
"scheduled": "المجدولة",
"boarding": "صعود",
"departed": "أقلعَت",
"landed": "هبوط",
"total_stay_price": "السعر الإجمالي للإقامة",
=======
>>>>>>> 4b446d46dc475c3831deb317bcd77dae800f209c
>>>>>>> b7aa1d88ca5ad71568b2755e0c90c1c795c2d72e
}
}

def apply_class_price(flight, ticket_class):
    base_price = float(flight.get("price", 120))

    class_multipliers = {
        "Economy": 1,
        "Premium Economy": 1.6,
        "Business": 3.2,
        "First": 5.5
    }

    if ticket_class == "Any":
        return flight

    multiplier = class_multipliers.get(ticket_class, 1)

    flight["class"] = ticket_class
    flight["price"] = round(base_price * multiplier, 2)

    return flight

def get_translation():
    lang = session.get("lang", "en")
    base = translations["en"].copy()
    selected = translations.get(lang, {})
    base.update(selected)
    return base
def translate_value(value):
    lang = session.get("lang", "en")
    t = translations.get(lang, translations["en"])

    if value is None:
        return ""

    value = str(value).strip()
    lower_value = value.lower()

    # BAGGAGE - catches English/French/Arabic saved values
    if "no checked bag" in lower_value or "aucun bagage" in lower_value or "بدون أمتعة" in value:
        return t.get("No checked bag", value)

    if "2 checked bags" in lower_value or "2 bagages" in lower_value or "حقيبتان" in value:
        return t.get("2 checked bags", value)

    if "1 checked bag" in lower_value or "1 bagage" in lower_value or "حقيبة مسجلة واحدة" in value:
        return t.get("1 checked bag", value)

    # REFUND REASON - catches English/French/Arabic saved values
    if "change of plans" in lower_value or "changement de plans" in lower_value or "تغيير الخطط" in value:
        return t.get("Change of plans", value)

    if value in t:
        return t[value]
    if "bagage en soute" in lower_value:
        return t.get("1 checked bag", value)

    if "standard meal" in lower_value or "repas standard" in lower_value or "وجبة عادية" in value:
         return t.get("Standard Meal", value)

    if "vegetarian meal" in lower_value or "repas végétarien" in lower_value or "وجبة نباتية" in value:
        return t.get("Vegetarian Meal", value)

    if "vegan meal" in lower_value or "repas végétalien" in lower_value or "وجبة نباتية صِرفة" in value:
        return t.get("Vegan Meal", value)
    if "standard taxi" in lower_value:
        return t.get("Standard Taxi", value)

    if "minivan" in lower_value:
        return t.get("Minivan", value)

    if "luxury car" in lower_value:
        return t.get("Luxury Car", value)

    if "meet & greet" in lower_value:
        return t.get("Meet & Greet + Luxury Transfer", value)

        return value

app.jinja_env.filters["tv"] = translate_value

def load_airports():
    airports = []
    seen_codes = set()

    file_path = os.path.join(BASE_DIR, "data", "airports.csv")

    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            iata = (row.get("iata_code") or "").strip().upper()
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

    return airports


AIRPORTS = load_airports()

SAMPLE_FLIGHTS = []

SAMPLE_HOTELS = []

AVIATIONSTACK_API_KEY = "96c825ec449994127cf418ff1869ab55"

def get_airport_from_code(code):
    code = (code or "").upper()
    for airport in AIRPORTS:
        if airport["code"].upper() == code:
            return airport
    return {
        "city": code,
        "name": f"{code} Airport",
        "code": code
    }

def get_real_flights(dep_iata, arr_iata, flight_date):
    url = "http://api.aviationstack.com/v1/flights"

    params = {
        "access_key": "96c825ec449994127cf418ff1869ab55",
        "dep_iata": dep_iata,
        "arr_iata": arr_iata
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        print("AVIATIONSTACK DATA:", data)
        print("AVIATIONSTACK RESPONSE:", data)
    except Exception as e:
        print("Aviationstack API error:", e)
        data = {}

    flights = []
    seen_departure_times = set()

    dep_airport = get_airport_from_code(dep_iata)
    arr_airport = get_airport_from_code(arr_iata)

    for item in data.get("data", []):
        departure = item.get("departure") or {}
        arrival = item.get("arrival") or {}
        airline = item.get("airline") or {}
        flight = item.get("flight") or {}

        dep_raw = departure.get("scheduled")
        arr_raw = arrival.get("scheduled")

        if not dep_raw or not arr_raw:
            continue

        try:
            departure_time = datetime.fromisoformat(dep_raw.replace("Z", "+00:00")).strftime("%H:%M")
            arrival_time = datetime.fromisoformat(arr_raw.replace("Z", "+00:00")).strftime("%H:%M")
        except:
            continue

        if departure_time in seen_departure_times:
            continue

        seen_departure_times.add(departure_time)

        airline_name = airline.get("name") or "AirGo Partner Airline"
        flight_number = flight.get("iata") or f"AG{1000 + len(flights) + 1}"

        flights.append({
            "id": len(flights) + 1,
            "airline": airline_name,
            "from": departure.get("airport") or dep_airport["name"],
            "from_city": dep_airport["city"],
            "from_code": departure.get("iata") or dep_iata,
            "airport_group": f"{dep_airport['city']} Airports",
            "to": arrival.get("airport") or arr_airport["name"],
            "to_city": arr_airport["city"],
            "to_code": arrival.get("iata") or arr_iata,
            "destination_group": f"{arr_airport['city']} Airports",
            "flight_number": flight_number,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "price": 120 + (len(flights) * 40),
            "class": "Economy",
            "seats_left": random.randint(3, 20),
            "stops": "Direct flight",
            "aircraft": "Boeing 737"
        })

        if len(flights) == 10:
            break

    return flights

RAPIDAPI_KEY = "ca2a3e15f8msh8bce0676a86b200p15b567jsnd7a9be5f0a49"
RAPIDAPI_HOST = "booking-com15.p.rapidapi.com"

def get_real_hotels(destination, check_in, check_out, guests=1):
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    destination_url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"

    destination_response = requests.get(
        destination_url,
        headers=headers,
        params={"query": destination},
        timeout=10
    )
    destination_data = destination_response.json()

    destination_results = (
        destination_data.get("data", [])
        or destination_data.get("data", {}).get("destinations", [])
        or destination_data.get("result", [])
    )

    if not destination_results:
        return []

    first_destination = destination_results[0]

    dest_id = first_destination.get("dest_id") or first_destination.get("id")
    search_type = first_destination.get("search_type") or first_destination.get("type") or "CITY"

    hotel_url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"

    hotel_response = requests.get(
        hotel_url,
        headers=headers,
        params={
            "dest_id": dest_id,
            "search_type": search_type,
            "arrival_date": check_in,
            "departure_date": check_out,
            "adults": guests,
            "room_qty": 1,
            "page_number": 1,
            "currency_code": session.get("currency", "GBP")
        },
        timeout=10
    )

    hotel_data = hotel_response.json()

    raw_hotels = (
        hotel_data.get("data", {}).get("hotels")
        or hotel_data.get("data", {}).get("result")
        or hotel_data.get("data")
        or []
    )

    hotels = []

    for index, item in enumerate(raw_hotels[:20], start=1):
        property_data = item.get("property", item)

        price_data = (
            property_data.get("priceBreakdown", {})
            .get("grossPrice", {})
        )

        hotel_name = (
            property_data.get("name")
            or property_data.get("hotel_name")
            or "Hotel"
        )

        price = (
            price_data.get("value")
            or property_data.get("price")
            or property_data.get("min_total_price")
            or 0
        )

        address = (
            property_data.get("address")
            or property_data.get("address_trans")
            or property_data.get("district")
            or property_data.get("wishlistName")
            or destination
        )

        hotels.append({
            "id": index,
            "name": hotel_name,
            "city": property_data.get("city") or property_data.get("wishlistName") or destination,
            "country": property_data.get("country") or property_data.get("countryCode", ""),
            "address": address,
            "latitude": property_data.get("latitude"),
            "longitude": property_data.get("longitude"),
            "stars": property_data.get("propertyClass", 4),
            "total_price": round(float(price or 0), 2),
            "room_types": ["Standard", "Deluxe", "Suite"],
            "description": property_data.get("reviewScoreWord") or "Hotel available for your trip"
        })

    return hotels

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

COUNTRY_NAME_ALIASES = {
    "GB": ["uk", "britain", "great britain", "england", "scotland", "wales", "sterling"],
    "US": ["usa", "us", "united states", "america", "american"],
    "AE": ["uae", "united arab emirates", "emirates", "emirati"],
    "TR": ["turkiye", "turkey", "turkish"],
    "IR": ["iran", "iranian"],
    "KR": ["south korea", "korea", "korean"],
    "RU": ["russia", "russian"],
    "VN": ["vietnam", "vietnamese"],
    "CZ": ["czech republic", "czechia"],
}

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
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
            requested_departure_airport TEXT DEFAULT '',
            requested_departure_city TEXT DEFAULT '',
            requested_departure_code TEXT DEFAULT '',
            requested_destination_airport TEXT DEFAULT '',
            requested_destination_city TEXT DEFAULT '',
            requested_destination_code TEXT DEFAULT '',
            passenger_count INTEGER NOT NULL DEFAULT 1,
            refund_reason TEXT DEFAULT '',
            refund_custom_reason TEXT DEFAULT '',
            refund_passengers INTEGER NOT NULL DEFAULT 0,
            refund_status TEXT NOT NULL DEFAULT 'None',
            refund_amount REAL NOT NULL DEFAULT 0,
            refund_processed INTEGER NOT NULL DEFAULT 0,
            original_price REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS hotel_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            flight_booking_id INTEGER NULL,
            hotel_name TEXT NOT NULL,
            hotel_city TEXT NOT NULL,
            hotel_country TEXT,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL,
            guests INTEGER NOT NULL,
            room_type TEXT,
            total_price REAL NOT NULL,
            booking_reference TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'CONFIRMED',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (flight_booking_id) REFERENCES bookings (id)
        )
    """)

    hotel_columns = [row["name"] for row in conn.execute("PRAGMA table_info(hotel_bookings)").fetchall()]

    hotel_missing_columns = {
        "refund_reason": "TEXT DEFAULT ''",
        "refund_custom_reason": "TEXT DEFAULT ''",
        "refund_status": "TEXT NOT NULL DEFAULT 'None'",
        "refund_amount": "REAL NOT NULL DEFAULT 0",
        "refund_processed": "INTEGER NOT NULL DEFAULT 0",
        "requested_check_in": "TEXT DEFAULT ''",
        "requested_check_out": "TEXT DEFAULT ''",
        "change_reason": "TEXT DEFAULT ''",
        "change_status": "TEXT NOT NULL DEFAULT 'None'",
    }

    for column_name, column_definition in hotel_missing_columns.items():
        if column_name not in hotel_columns:
            conn.execute(f"ALTER TABLE hotel_bookings ADD COLUMN {column_name} {column_definition}")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS booking_change_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            booking_type TEXT NOT NULL DEFAULT 'flight',
            request_type TEXT NOT NULL,
            requested_value TEXT,
            notes TEXT,
            status TEXT NOT NULL DEFAULT 'PENDING',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    booking_columns = [row["name"] for row in conn.execute("PRAGMA table_info(bookings)").fetchall()]
    missing_columns = {
        "passenger_count": "INTEGER NOT NULL DEFAULT 1",
        "refund_reason": "TEXT DEFAULT ''",
        "refund_custom_reason": "TEXT DEFAULT ''",
        "refund_passengers": "INTEGER NOT NULL DEFAULT 0",
        "refund_status": "TEXT NOT NULL DEFAULT 'None'",
        "refund_amount": "REAL NOT NULL DEFAULT 0",
        "refund_processed": "INTEGER NOT NULL DEFAULT 0",
        "original_price": "REAL NOT NULL DEFAULT 0",
        "refund_passenger_ids": "TEXT DEFAULT ''",
    }

    for column_name, column_definition in missing_columns.items():
        if column_name not in booking_columns:
            conn.execute(f"ALTER TABLE bookings ADD COLUMN {column_name} {column_definition}")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS passengers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            passport_number TEXT NOT NULL,
            assistance_required TEXT DEFAULT '',
            assistance_options TEXT DEFAULT '',
            other_assistance TEXT DEFAULT '',
            baggage TEXT DEFAULT 'No checked bag',
            meal_choice TEXT DEFAULT 'No Meal',
            baggage_price REAL NOT NULL DEFAULT 0,
            seat TEXT NOT NULL,
            FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
        )
    """)

    passenger_columns = [row["name"] for row in conn.execute("PRAGMA table_info(passengers)").fetchall()]
    passenger_missing_columns = {
        "baggage": "TEXT DEFAULT 'No checked bag'",
        "meal_choice": "TEXT DEFAULT 'No Meal'",
        "baggage_price": "REAL NOT NULL DEFAULT 0",
        "status": "TEXT NOT NULL DEFAULT 'Active'",
        "changed_departure_airport": "TEXT DEFAULT ''",
        "changed_departure_city": "TEXT DEFAULT ''",
        "changed_departure_code": "TEXT DEFAULT ''",
        "changed_destination_airport": "TEXT DEFAULT ''",
        "changed_destination_city": "TEXT DEFAULT ''",
        "changed_destination_code": "TEXT DEFAULT ''",
        "changed_flight_date": "TEXT DEFAULT ''",
        "ticket_class": "TEXT DEFAULT ''",
        "upgrade_cost": "REAL NOT NULL DEFAULT 0",
        "priority_boarding": "INTEGER NOT NULL DEFAULT 0",
        "wifi_package": "INTEGER NOT NULL DEFAULT 0",
        "lounge_access": "INTEGER NOT NULL DEFAULT 0",
    }

    for column_name, column_definition in passenger_missing_columns.items():
        if column_name not in passenger_columns:
            conn.execute(f"ALTER TABLE passengers ADD COLUMN {column_name} {column_definition}")

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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            airline TEXT NOT NULL,
            departure_airport TEXT NOT NULL,
            departure_city TEXT NOT NULL,
            departure_code TEXT NOT NULL,
            destination_airport TEXT NOT NULL,
            destination_city TEXT NOT NULL,
            destination_code TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            arrival_time TEXT NOT NULL,
            base_price REAL NOT NULL,
            ticket_class TEXT NOT NULL,
            seats_left INTEGER NOT NULL DEFAULT 0
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS booking_flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            flight_order INTEGER NOT NULL,
            airline TEXT NOT NULL,
            flight_number TEXT DEFAULT '',
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
            seat TEXT DEFAULT '',
            FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
        )
    """)

    booking_flight_columns = [row["name"] for row in conn.execute("PRAGMA table_info(booking_flights)").fetchall()]

    if "flight_number" not in booking_flight_columns:
        conn.execute("ALTER TABLE booking_flights ADD COLUMN flight_number TEXT DEFAULT ''")

    flight_count = conn.execute("SELECT COUNT(*) as cnt FROM flights").fetchone()["cnt"]
    if flight_count == 0:
        conn.executemany("""
            INSERT INTO flights (
                airline, departure_airport, departure_city, departure_code,
                destination_airport, destination_city, destination_code,
                departure_time, arrival_time, base_price, ticket_class, seats_left
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            ("AirGo", "London Heathrow", "London", "LHR", "Paris Charles de Gaulle", "Paris", "CDG", "08:00", "10:15", 120, "Economy", 14),
            ("AirGo", "London Gatwick", "London", "LGW", "Paris Orly", "Paris", "ORY", "12:30", "14:45", 185, "Premium Economy", 7),
            ("AirGo", "London Stansted", "London", "STN", "Dubai International", "Dubai", "DXB", "18:20", "03:35", 310, "Business", 3),
            ("AirGo", "Paris Charles de Gaulle", "Paris", "CDG", "Dubai International", "Dubai", "DXB", "09:45", "18:10", 275, "Economy", 11),
            ("AirGo", "Dubai International", "Dubai", "DXB", "London Heathrow", "London", "LHR", "14:00", "18:45", 420, "Business", 5),
            ("AirGo", "London City", "London", "LCY", "John F. Kennedy", "New York", "JFK", "10:00", "13:25", 510, "Premium Economy", 8),
        ])

    conn.execute("CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS taxi_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            booking_reference TEXT NOT NULL UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            alt_phone TEXT DEFAULT \'\',
            email TEXT NOT NULL,
            transfer_type TEXT NOT NULL,
            pickup TEXT NOT NULL,
            dropoff TEXT NOT NULL,
            distance_km REAL NOT NULL,
            duration TEXT NOT NULL,
            price REAL NOT NULL,
            booking_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT \'Confirmed\',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()


def generate_booking_reference(length=8):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def db_flight_to_dict(flight):
    """Convert a database flight row to the dict format used by templates."""
    if flight is None:
        return None
    return {
        "id": flight["id"],
        "airline": flight["airline"],
        "from": flight["departure_airport"],
        "from_city": flight["departure_city"],
        "from_code": flight["departure_code"],
        "to": flight["destination_airport"],
        "to_city": flight["destination_city"],
        "to_code": flight["destination_code"],
        "departure_time": flight["departure_time"],
        "arrival_time": flight["arrival_time"],
        "price": flight["base_price"],
        "class": flight["ticket_class"],
        "seats_left": flight["seats_left"]
    }


def find_flight_by_id(flight_id):
    last_flights = session.get("last_flights", [])

    for flight in last_flights:
        if int(flight["id"]) == int(flight_id):
            return flight

    conn = get_db_connection()
    flight = conn.execute("""
        SELECT id, airline, departure_airport, departure_city, departure_code,
               destination_airport, destination_city, destination_code,
               departure_time, arrival_time, base_price, ticket_class, seats_left
        FROM flights
        WHERE id = ?
    """, (flight_id,)).fetchone()
    conn.close()

    return db_flight_to_dict(flight)


def find_hotel_by_id(hotel_id):
    hotels = session.get("last_hotels", [])

    for hotel in hotels:
        if int(hotel["id"]) == int(hotel_id):
            return hotel

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
    flight_date = session.get("search_data", {}).get("depart_date", "")
    conn = get_db_connection()

    passenger_rows = conn.execute("""
        SELECT passengers.seat
        FROM passengers
        JOIN bookings ON passengers.booking_id = bookings.id
        WHERE bookings.airline = ?
          AND bookings.departure_airport = ?
          AND bookings.destination_airport = ?
          AND bookings.departure_time = ?
          AND bookings.arrival_time = ?
          AND bookings.flight_date = ?
          AND bookings.flight_status != 'Cancelled'
    """, (
        flight["airline"],
        flight["from"],
        flight["to"],
        flight["departure_time"],
        flight["arrival_time"],
        flight_date
    )).fetchall()

    legacy_rows = conn.execute("""
        SELECT seat FROM bookings
        WHERE airline = ?
          AND departure_airport = ?
          AND destination_airport = ?
          AND departure_time = ?
          AND arrival_time = ?
          AND flight_date = ?
          AND flight_status != 'Cancelled'
    """, (
        flight["airline"],
        flight["from"],
        flight["to"],
        flight["departure_time"],
        flight["arrival_time"],
        flight_date
    )).fetchall()

    conn.close()

    booked = {row["seat"] for row in passenger_rows if row["seat"]}
    for row in legacy_rows:
        if row["seat"]:
            for seat in str(row["seat"]).split(","):
                seat = seat.strip()
                if seat:
                    booked.add(seat)

    return booked


def get_seat_layout():
    return [
        {
            "cabin": "First Class",
            "rows": range(1, 3),
            "color_class": "first-class",
            "seat_letters": ["A", "D", "F", "K"],
            "availability_rate": 0.55
        },
        {
            "cabin": "Business Class",
            "rows": range(3, 8),
            "color_class": "business-class",
            "seat_letters": ["A", "B", "D", "E", "F", "K"],
            "availability_rate": 0.65
        },
        {
            "cabin": "Premium Economy",
            "rows": range(8, 11),
            "color_class": "premium-class",
            "seat_letters": ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K"],
            "availability_rate": 0.72
        },
        {
            "cabin": "Economy",
            "rows": range(11, 21),
            "color_class": "economy-class",
            "seat_letters": ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K"],
            "availability_rate": 0.78
        }
    ]


def get_seat_type_and_price(seat_code, row_number, seat_letter, cabin_name):
    if cabin_name == "First Class":
        if row_number in [1, 2]:
            return "Suite", 60
        if seat_letter in ["A", "K"]:
            return "Window", 45
        return "Aisle", 40

    if cabin_name == "Business Class":
        if seat_letter in ["A", "K"]:
            return "Window", 30
        if seat_letter in ["D", "E"]:
            return "Aisle", 28
        return "Middle", 24

    if cabin_name == "Premium Economy":
        if row_number in [10]:
            return "Emergency Exit", 25
        if seat_letter in ["A", "K"]:
            return "Window", 18
        if seat_letter in ["C", "D", "G", "H"]:
            return "Aisle", 15
        return "Middle", 12

    if row_number in [10, 11]:
        return "Emergency Exit", 25
    if seat_letter in ["A", "K"]:
        return "Window", 10
    if seat_letter in ["C", "D", "G", "H"]:
        return "Aisle", 8
    return "Middle", 5


def generate_seeded_unavailable_seats(flight, flight_date, booked_seats):
    layout = get_seat_layout()
    unavailable = set()

    seed_string = (
        f"{flight['airline']}-"
        f"{flight['from_code']}-"
        f"{flight['to_code']}-"
        f"{flight['departure_time']}-"
        f"{flight['arrival_time']}-"
        f"{flight_date}"
    )

    seed_number = int(hashlib.md5(seed_string.encode()).hexdigest(), 16)
    rng = random.Random(seed_number)

    for cabin in layout:
        for row_number in cabin["rows"]:
            for seat_letter in cabin["seat_letters"]:
                seat_code = f"{row_number}{seat_letter}"

                if seat_code in booked_seats:
                    continue

                if rng.random() > cabin["availability_rate"]:
                    unavailable.add(seat_code)

    return unavailable


def generate_seat_map(flight):
    flight_date = session.get("search_data", {}).get("depart_date", "")
    booked_seats = get_booked_seats_for_flight(flight)
    random_unavailable = generate_seeded_unavailable_seats(flight, flight_date, booked_seats)
    all_unavailable = booked_seats.union(random_unavailable)

    sections = []

    for cabin in get_seat_layout():
        cabin_rows = []

        for row_number in cabin["rows"]:
            row_seats = []

            for seat_letter in cabin["seat_letters"]:
                seat_code = f"{row_number}{seat_letter}"
                seat_type, seat_price = get_seat_type_and_price(seat_code, row_number, seat_letter, cabin["cabin"])

                row_seats.append({
                    "seat": seat_code,
                    "letter": seat_letter,
                    "type": seat_type,
                    "price": seat_price,
                    "available": seat_code not in all_unavailable
                })

            cabin_rows.append({
                "row_number": row_number,
                "seats": row_seats
            })

        sections.append({
            "cabin": cabin["cabin"],
            "color_class": cabin["color_class"],
            "rows": cabin_rows
        })

    return sections


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
            next_tier = LOYALTY_TIERS[idx + 1] if idx + 1 < len(LOYALTY_TIERS) else None

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


def normalize_place_name(text):
    text = (text or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_airport_selection(selection_text):
    selection_text = (selection_text or "").strip()
    if not selection_text:
        return None

    match = re.search(r"\(([A-Z]{3})\)", selection_text)
    if not match:
        return None

    selected_code = match.group(1).upper()

    for airport in AIRPORTS:
        if airport["code"].upper() == selected_code:
            return airport

    return None


def apply_approved_change_to_booking(conn, booking):
    updated_departure_airport = booking["departure_airport"]
    updated_departure_city = booking["departure_city"]
    updated_departure_code = booking["departure_code"]
    updated_destination_airport = booking["destination_airport"]
    updated_destination_city = booking["destination_city"]
    updated_destination_code = booking["destination_code"]
    updated_flight_date = booking["flight_date"]

    requested_date = (booking["requested_date"] or "").strip()

    if booking["requested_departure_airport"] and booking["requested_departure_city"] and booking["requested_departure_code"]:
        updated_departure_airport = booking["requested_departure_airport"]
        updated_departure_city = booking["requested_departure_city"]
        updated_departure_code = booking["requested_departure_code"]

    if booking["requested_destination_airport"] and booking["requested_destination_city"] and booking["requested_destination_code"]:
        updated_destination_airport = booking["requested_destination_airport"]
        updated_destination_city = booking["requested_destination_city"]
        updated_destination_code = booking["requested_destination_code"]

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
    today = date.today().isoformat()
    t = get_translation()
    return render_template("index.html", today=today, t=t)


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

    exact_city_matches = []
    code_matches = []
    name_matches = []

    for airport in AIRPORTS:
        city_lower = airport["city"].lower()
        name_lower = airport["name"].lower()
        code_lower = airport["code"].lower()

        if city_lower.startswith(query):
            exact_city_matches.append(airport)
        elif code_lower.startswith(query):
            code_matches.append(airport)
        elif query in name_lower or query in city_lower:
            name_matches.append(airport)

    matches = exact_city_matches + code_matches + name_matches

    seen = set()
    unique_matches = []
    for airport in matches:
        if airport["code"] not in seen:
            seen.add(airport["code"])
            unique_matches.append(airport)

    return jsonify(unique_matches[:10])

def apply_class_price(flight, ticket_class):
    base_price = float(flight.get("price", 120))

    class_multipliers = {
        "Economy": 1,
        "Premium Economy": 1.6,
        "Business": 3.2,
        "First": 5.5
    }

    if ticket_class == "Any":
        return flight

    multiplier = class_multipliers.get(ticket_class, 1)

    flight["class"] = ticket_class
    flight["price"] = round(base_price * multiplier, 2)

    return flight

@app.route("/results", methods=["GET", "POST"])
def results():
    if request.method == "POST":
        trip_type = request.form.get("trip_type", "return")
        passengers = request.form.get("passengers", "1")
        ticket_class = request.form.get("ticket_class", "Any")

        departure = request.form.get("departure", "").strip()
        destination = request.form.get("destination", "").strip()
        depart_date = request.form.get("depart_date", "")
        return_date = request.form.get("return_date", "")

        multi_departures = request.form.getlist("multi_departure[]")
        multi_destinations = request.form.getlist("multi_destination[]")
        multi_depart_dates = request.form.getlist("multi_depart_date[]")

        if trip_type == "multi_city":
            multi_flights = []

            for i in range(len(multi_departures)):
                if multi_departures[i].strip() and multi_destinations[i].strip() and multi_depart_dates[i].strip():
                    multi_flights.append({
                        "departure": multi_departures[i].strip(),
                        "destination": multi_destinations[i].strip(),
                        "depart_date": multi_depart_dates[i].strip()
                    })

            if not multi_flights:
                flash("Please enter at least one multi-city flight.", "error")
                return redirect(url_for("home"))

            first_leg = multi_flights[0]

            departure_airport = parse_airport_selection(first_leg["departure"])
            destination_airport = parse_airport_selection(first_leg["destination"])

            if not departure_airport or not destination_airport:
                flash("Please select airports from the suggestions.", "error")
                return redirect(url_for("home"))

            matching_flights = get_real_flights(
                departure_airport["code"],
                destination_airport["code"],
                first_leg["depart_date"]
            )

            search_data = {
                "trip_type": trip_type,
                "departure": first_leg["departure"],
                "destination": first_leg["destination"],
                "depart_date": first_leg["depart_date"],
                "return_date": "",
                "passengers": passengers,
                "ticket_class": ticket_class,
                "multi_flights": multi_flights
            }

        else:
            departure_airport = parse_airport_selection(departure)
            destination_airport = parse_airport_selection(destination)

            if not departure_airport or not destination_airport:
                flash("Please select airports from the suggestions.", "error")
                return redirect(url_for("home"))

            matching_flights = get_real_flights(
                departure_airport["code"],
                destination_airport["code"],
                depart_date
            )

            search_data = {
                "trip_type": trip_type,
                "departure": departure,
                "destination": destination,
                "depart_date": depart_date,
                "return_date": return_date,
                "passengers": passengers,
                "ticket_class": ticket_class,
                "multi_flights": []
            }

        if ticket_class != "Any":
            matching_flights = [
                apply_class_price(flight, ticket_class)
                for flight in matching_flights
            ]

        session["search_data"] = search_data
        session["last_flights"] = matching_flights
        session["selected_flights"] = []
        session.pop("selected_flight", None)

        return render_template(
            "results.html",
            flights=matching_flights,
            search_data=search_data,
            class_benefits=CLASS_BENEFITS,
            t=get_translation()
        )

    search_data = session.get("search_data")
    matching_flights = session.get("last_flights")

    if not search_data or matching_flights is None:
        flash("Please search for flights first.", "error")
        return redirect(url_for("home"))

    return render_template(
        "results.html",
        flights=matching_flights,
        search_data=search_data,
        class_benefits=CLASS_BENEFITS,
        t=get_translation()
    )

@app.route("/select-flight/<int:flight_id>")
def select_flight(flight_id):
    last_flights = session.get("last_flights", [])
    selected_flight = None

    for flight in last_flights:
        if int(flight["id"]) == int(flight_id):
            selected_flight = flight
            break

    if not selected_flight:
        flash("Selected flight was not found.", "error")
        return redirect(url_for("home"))

    search_data = session.get("search_data", {})
    trip_type = search_data.get("trip_type", "one_way")

    selected_flights = session.get("selected_flights", [])
    selected_flights.append(selected_flight)
    session["selected_flights"] = selected_flights

    if trip_type == "return" and len(selected_flights) == 1:
        return redirect(url_for("return_results"))

    if trip_type == "multi_city":
        multi_flights = search_data.get("multi_flights", [])
        if len(selected_flights) < len(multi_flights):
            return redirect(url_for("multi_city_results"))

    session["selected_flight"] = selected_flights[0]
    session["selected_flights"] = selected_flights

    return redirect(url_for("passenger_details", flight_id=selected_flights[0]["id"]))

@app.route("/return-results")
def return_results():
    search_data = session.get("search_data", {})
    selected_flights = session.get("selected_flights", [])

    if not search_data or not selected_flights:
        flash("Please select your outbound flight first.", "error")
        return redirect(url_for("home"))

    departure_airport = parse_airport_selection(search_data.get("departure", ""))
    destination_airport = parse_airport_selection(search_data.get("destination", ""))
    return_date = search_data.get("return_date", "")

    if not departure_airport or not destination_airport or not return_date:
        flash("Return flight details are missing.", "error")
        return redirect(url_for("home"))

    matching_flights = get_real_flights(
        destination_airport["code"],
        departure_airport["code"],
        return_date
    )

    ticket_class = search_data.get("ticket_class", "Any")

    if ticket_class != "Any":
        matching_flights = [
            apply_class_price(flight, ticket_class)
            for flight in matching_flights
        ]

    session["last_flights"] = matching_flights
    session["current_selection_stage"] = "return"

    return render_template(
        "results.html",
        flights=matching_flights,
        search_data={
            **search_data,
            "departure": search_data.get("destination"),
            "destination": search_data.get("departure"),
            "depart_date": return_date
        },
        class_benefits=CLASS_BENEFITS,
        t=get_translation()
    )


@app.route("/multi-city-results")
def multi_city_results():
    search_data = session.get("search_data", {})
    selected_flights = session.get("selected_flights", [])
    multi_flights = search_data.get("multi_flights", [])

    if not search_data:
        flash("Please search for flights first.", "error")
        return redirect(url_for("home"))

    next_index = len(selected_flights)

    if next_index >= len(multi_flights):
        return redirect(url_for("passenger_details", flight_id=selected_flights[0]["id"]))

    next_leg = multi_flights[next_index]

    departure_airport = parse_airport_selection(next_leg.get("departure", ""))
    destination_airport = parse_airport_selection(next_leg.get("destination", ""))

    if not departure_airport or not destination_airport:
        flash("Multi-city flight details are missing.", "error")
        return redirect(url_for("home"))

    matching_flights = get_real_flights(
        departure_airport["code"],
        destination_airport["code"],
        next_leg.get("depart_date", "")
    )

    ticket_class = search_data.get("ticket_class", "Any")

    if ticket_class != "Any":
        matching_flights = [
            apply_class_price(flight, ticket_class)
            for flight in matching_flights
        ]

    session["last_flights"] = matching_flights
    session["current_selection_stage"] = f"multi_city_{next_index + 1}"

    return render_template(
        "results.html",
        flights=matching_flights,
        search_data={
            **search_data,
            "departure": next_leg.get("departure"),
            "destination": next_leg.get("destination"),
            "depart_date": next_leg.get("depart_date")
        },
        class_benefits=CLASS_BENEFITS,
        t=get_translation()
    )
    

@app.route("/passenger-details/<int:flight_id>", methods=["GET", "POST"])
def passenger_details(flight_id):

    last_flights = session.get("last_flights", [])
    selected_flight = session.get("selected_flight")
    selected_flights = session.get("selected_flights", [selected_flight])

    for flight in last_flights:
        if int(flight["id"]) == int(flight_id):
            selected_flight = flight
            break

    if not selected_flight:
        selected_flight = find_flight_by_id(flight_id)

    if not selected_flight:
        flash("Selected flight was not found.", "error")
        return redirect(url_for("home"))

    search_data = session.get("search_data", {})
    passenger_count = int(search_data.get("passengers", 1) or 1)
    passenger_count = max(1, passenger_count)

    if request.method == "POST":
        passengers = []

        for i in range(1, passenger_count + 1):
            assistance_options = request.form.getlist(f"assistance_options_{i}")

            passenger = {
                "first_name": request.form.get(f"first_name_{i}", "").strip(),
                "last_name": request.form.get(f"last_name_{i}", "").strip(),
                "email": request.form.get(f"email_{i}", "").strip(),
                "phone": request.form.get(f"phone_{i}", "").strip(),
                "passport_number": request.form.get(f"passport_number_{i}", "").strip(),
                "assistance_required": request.form.get(f"assistance_required_{i}", ""),
                "assistance_options": assistance_options,
                "other_assistance": request.form.get(f"other_assistance_{i}", "").strip()
            }

            required_fields = [
                passenger["first_name"],
                passenger["last_name"],
                passenger["email"],
                passenger["phone"],
                passenger["passport_number"],
            ]

            if not all(required_fields):
                flash(f"Please fill in all details for passenger {i}.", "error")
                return render_template(
                    "passenger_details.html",
                    flight=selected_flight,
                    benefits=CLASS_BENEFITS.get(selected_flight["class"], {}),
                    passenger_count=passenger_count,
                    t=get_translation()
                )

            passengers.append(passenger)

        session["selected_flight"] = selected_flight
        session["passenger_data"] = passengers
        session.pop("selected_seat", None)
        session.pop("selected_seats", None)

        if not session.get("user_id"):
            session["post_login_redirect"] = url_for("extras")
            flash("Please log in or sign up to continue your booking.", "error")
            return redirect(url_for("login"))

        return redirect(url_for("extras"))

    return render_template(
        "passenger_details.html",
        flight=selected_flight,
        benefits=CLASS_BENEFITS.get(selected_flight["class"], {}),
        passenger_count=passenger_count,
        selected_flights=selected_flights,
        t=get_translation()
    )


@app.route("/extras", methods=["GET", "POST"])
def extras():
    selected_flight = session.get("selected_flight")
    selected_flights = session.get("selected_flights", [selected_flight])
    passengers = session.get("passenger_data", [])

    if not selected_flight or not passengers:
        flash("Please select a flight and enter passenger details first.", "error")
        return redirect(url_for("home"))

    passenger_count = len(passengers)

    def baggage_price_from_choice(choice):
        if "1 checked bag" in choice:
            return 30
        if "2 checked bags" in choice:
            return 60
        return 0

    if request.method == "POST":
        passenger_extras = []

        for i, passenger in enumerate(passengers, start=1):
            baggage = request.form.get(f"baggage_{i}", "No checked bag")
            meal_choice = request.form.get(f"meal_choice_{i}", "No Meal")
            passenger_extras.append({
                "passenger_number": i,
                "first_name": passenger.get("first_name", ""),
                "last_name": passenger.get("last_name", ""),
                "baggage": baggage,
                "meal_choice": meal_choice,
                "baggage_price": baggage_price_from_choice(baggage)
            })

        insurance = request.form.get("insurance", "No Travel Insurance")

        baggage_summary = ", ".join([
            f"Passenger {item['passenger_number']}: {item['baggage']}"
            for item in passenger_extras
        ])
        meal_summary = ", ".join([
            f"Passenger {item['passenger_number']}: {item['meal_choice']}"
            for item in passenger_extras
        ])

        session["extras"] = {
            "passenger_extras": passenger_extras,
            "insurance": insurance,
            "baggage": baggage_summary,
            "meal_choice": meal_summary,
            "total_baggage_price": sum(item["baggage_price"] for item in passenger_extras)
        }

        return redirect(url_for("seat_selection"))

    return render_template(
        "extras.html",
        flight=selected_flight,
        passengers=passengers,
        passenger_count=passenger_count,
        selected_flights=selected_flights,
        t=get_translation()
    )

@app.route("/seat-selection", methods=["GET", "POST"])
def seat_selection():
    selected_flight = session.get("selected_flight")
    selected_flights = session.get("selected_flights", [selected_flight])
    passengers = session.get("passenger_data")

    if not selected_flight or not passengers:
        flash("Please select a flight and enter passenger details first.", "error")
        return redirect(url_for("home"))

    passenger_count = len(passengers)

    if request.method == "POST":
        selected_seats_by_flight = []

        for flight_index, flight in enumerate(selected_flights):
            flight_seats = []

            for passenger_index in range(1, passenger_count + 1):
                seat = request.form.get(f"seat_{flight_index}_{passenger_index}", "").strip()

                if not seat:
                    flash("Please choose seats for every passenger on every flight.", "error")
                    seat_maps = [generate_seat_map(f) for f in selected_flights]
                    return render_template(
                        "seat_selection.html",
                        flight=selected_flight,
                        selected_flights=selected_flights,
                        seat_maps=seat_maps,
                        passengers=passengers,
                        passenger_count=passenger_count,
                        t=get_translation()
                    )

                flight_seats.append(seat)

            if len(set(flight_seats)) != len(flight_seats):
                flash("Please choose different seats for each passenger on the same flight.", "error")
                seat_maps = [generate_seat_map(f) for f in selected_flights]
                return render_template(
                    "seat_selection.html",
                    flight=selected_flight,
                    selected_flights=selected_flights,
                    seat_maps=seat_maps,
                    passengers=passengers,
                    passenger_count=passenger_count,
                    t=get_translation()
                )

            selected_seats_by_flight.append(flight_seats)

        session["selected_seats_by_flight"] = selected_seats_by_flight

        flat_seats = []
        for flight_seats in selected_seats_by_flight:
            flat_seats.extend(flight_seats)

        session["selected_seats"] = flat_seats
        session["selected_seat"] = ", ".join(flat_seats)

        return redirect(url_for("review_booking"))

    seat_maps = [generate_seat_map(f) for f in selected_flights]

    return render_template(
        "seat_selection.html",
        flight=selected_flight,
        selected_flights=selected_flights,
        seat_maps=seat_maps,
        passengers=passengers,
        passenger_count=passenger_count,
        t=get_translation()
    )


@app.route("/review-booking")
def review_booking():
    selected_flight = session.get("selected_flight")
    selected_flights = session.get("selected_flights", [selected_flight])
    passengers = session.get("passenger_data")
    selected_seats = session.get("selected_seats")
    selected_seats_by_flight = session.get("selected_seats_by_flight")
    search_data = session.get("search_data", {})
    extras = session.get("extras", {})

    if not selected_flight or not passengers or not selected_seats_by_flight:
        flash("Please complete passenger details and seat selection first.", "error")
        return redirect(url_for("home"))

    return render_template(
        "review_booking.html",
        flight=selected_flight,
        selected_flights=selected_flights,
        passengers=passengers,
        passenger=passengers[0],
        selected_seats=selected_seats,
        selected_seat=", ".join(selected_seats or []),
        selected_seats_by_flight=selected_seats_by_flight,
        search_data=search_data,
        extras=extras,
        t=get_translation()
    )


def get_seat_price_and_type(selected_flight, selected_seat):
    seat_sections = generate_seat_map(selected_flight)
    for section in seat_sections:
        for row in section["rows"]:
            for seat in row["seats"]:
                if seat["seat"] == selected_seat:
                    return seat["price"], seat["type"]
    return 0, ""

def calculate_price(selected_flight, extras, selected_seats):
    selected_flights = session.get("selected_flights", [])
    passengers = session.get("passenger_data", [])

    if not selected_flights:
        selected_flights = [selected_flight]

    passenger_count = len(passengers) if passengers else 1

    base_fare = sum(float(flight["price"]) for flight in selected_flights) * passenger_count

    passenger_extras = extras.get("passenger_extras", [])
    baggage_price = sum(float(item.get("baggage_price", 0) or 0) for item in passenger_extras)

    insurance_price = 25 if "Insurance" in extras.get("insurance", "") else 0

    seat_price = 0
    seat_types = []

    selected_seats_by_flight = session.get("selected_seats_by_flight", [])

    for flight_index, flight in enumerate(selected_flights):
        if flight_index < len(selected_seats_by_flight):
            for seat_code in selected_seats_by_flight[flight_index]:
                current_price, current_type = get_seat_price_and_type(flight, seat_code)
                seat_price += current_price
                seat_types.append(current_type)

    total_price = base_fare + baggage_price + insurance_price + seat_price

    return {
        "base_fare": base_fare,
        "baggage_price": baggage_price,
        "insurance_price": insurance_price,
        "seat_price": seat_price,
        "seat_type": ", ".join([seat_type for seat_type in seat_types if seat_type]),
        "total_price": total_price,
    }

@app.route("/payment", methods=["GET", "POST"])
def payment():
    selected_flight = session.get("selected_flight")
    selected_flights = session.get("selected_flights") or ([selected_flight] if selected_flight else [])
    passengers = session.get("passenger_data")
    selected_seats = session.get("selected_seats")
    search_data = session.get("search_data", {})
    extras = session.get("extras", {})

    if not selected_flight or not selected_flights or not passengers:
        flash("Please select a flight and enter passenger details first.", "error")
        return redirect(url_for("home"))

    if not selected_seats:
        flash("Please choose seats before payment.", "error")
        return redirect(url_for("seat_selection"))

    if not session.get("user_id"):
        session["post_login_redirect"] = url_for("payment")
        flash("Please log in to complete your booking.", "error")
        return redirect(url_for("login"))

    price_data = calculate_price(selected_flight, extras, selected_seats)
    base_points_earned = calculate_points(price_data["base_fare"])

    conn = get_db_connection()
    current_points = conn.execute("""
        SELECT COALESCE(SUM(points_earned), 0) AS total_points
        FROM bookings
        WHERE user_id = ?
    """, (session["user_id"],)).fetchone()["total_points"]
    conn.close()

    available_points = current_points
    max_discount = min(available_points // 100, int(price_data["total_price"]))

    point_options = []
    for discount in range(5, max_discount + 1, 5):
        point_options.append({
            "points": discount * 100,
            "discount": discount
        })

    def render_payment(points_used=0, points_discount=0, final_price=None):
       return render_template(
    "payment.html",
    flight=selected_flight,
    selected_flights=selected_flights,
    passengers=passengers,
    passenger=passengers[0],
    selected_seats=selected_seats,
    selected_seat=", ".join(selected_seats),
    extras=extras,
    search_data=search_data,
    current_points=current_points,
    available_points=available_points,
    point_options=point_options,
    points_used=points_used,
    points_discount=points_discount,
    final_price=final_price if final_price is not None else price_data["total_price"],
    current_month=datetime.now().strftime("%Y-%m"),
    **price_data
)
    if request.method == "POST":
        points_used = int(request.form.get("points_to_use", 0) or 0)

        if points_used < 0:
            points_used = 0

        if points_used > current_points:
            flash("You do not have enough points for that discount.", "error")
            return redirect(url_for("payment"))

        points_discount = points_used / 100
        final_price = max(0, price_data["total_price"] - points_discount)

        payment_data = {
            "card_name": request.form.get("card_name", "").strip(),
            "card_number": request.form.get("card_number", "").strip(),
            "expiry_date": request.form.get("expiry_date", "").strip(),
            "cvv": request.form.get("cvv", "").strip()
        }

        if not request.form.get("accept_terms"):
            flash("You must accept the Terms & Conditions before completing your booking.", "error")
            return render_payment(points_used, points_discount, final_price)

        if not all(payment_data.values()):
            flash("Please fill in all payment fields.", "error")
            return render_payment(points_used, points_discount, final_price)

        booking_reference = generate_booking_reference()
        flight_date = search_data.get("depart_date", "")
        return_date = search_data.get("return_date", "")
        passenger_count = len(passengers)
        main_passenger = passengers[0]
        seat_summary = ", ".join(selected_seats)
        passenger_extras = extras.get("passenger_extras", [])
        meal_summary = extras.get("meal_choice", "No Meal")

        outbound_flight = selected_flights[0]
        return_flight = selected_flights[1] if len(selected_flights) > 1 else None

        airline_text = " + ".join(sorted(set(flight["airline"] for flight in selected_flights)))

        departure_airport_text = outbound_flight["from"]
        departure_city_text = outbound_flight["from_city"]
        departure_code_text = outbound_flight["from_code"]

        destination_airport_text = outbound_flight["to"]
        destination_city_text = outbound_flight["to_city"]
        destination_code_text = outbound_flight["to_code"]

        departure_time_text = outbound_flight["departure_time"]
        arrival_time_text = outbound_flight["arrival_time"]

        if return_flight:
            departure_time_text = outbound_flight["departure_time"] + " - " + return_flight["departure_time"]
            arrival_time_text = outbound_flight["arrival_time"] + " - " + return_flight["arrival_time"]

        total_checked_bags = 0
        for item in passenger_extras:
            if "1 checked bag" in item.get("baggage", ""):
                total_checked_bags += 1
            elif "2 checked bags" in item.get("baggage", ""):
                total_checked_bags += 2

        points_earned = max(0, base_points_earned - points_used)

        conn = get_db_connection()
        cursor = conn.execute("""
            INSERT INTO bookings (
                user_id, booking_reference, first_name, last_name, email, phone, passport_number,
                airline, departure_airport, departure_city, departure_code, destination_airport,
                destination_city, destination_code, flight_date, departure_time, arrival_time,
                ticket_class, meal_choice, seat, price, points_earned, trip_type, change_request,
                change_status, flight_status, extra_baggage, priority_boarding, wifi_package,
                lounge_access, requested_route, requested_date, requested_departure_airport,
                requested_departure_city, requested_departure_code, requested_destination_airport,
                requested_destination_city, requested_destination_code, passenger_count,
                refund_reason, refund_custom_reason, refund_passengers, refund_status,
                refund_amount, refund_processed, original_price
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            booking_reference,
            main_passenger["first_name"],
            main_passenger["last_name"],
            main_passenger["email"],
            main_passenger["phone"],
            main_passenger["passport_number"],
            airline_text,
            departure_airport_text,
            departure_city_text,
            departure_code_text,
            destination_airport_text,
            destination_city_text,
            destination_code_text,
            flight_date,
            departure_time_text,
            arrival_time_text,
            outbound_flight["class"],
            meal_summary,
            seat_summary,
            final_price,
            points_earned,
            search_data.get("trip_type", "return"),
            "",
            "None",
            DEFAULT_FLIGHT_STATUS,
            total_checked_bags,
            0,
            0,
            0,
            "",
            return_date,
            "",
            "",
            "",
            "",
            "",
            "",
            passenger_count,
            "",
            "",
            0,
            "None",
            0,
            0,
            final_price
        ))

        booking_id = cursor.lastrowid

        selected_seats_by_flight = session.get("selected_seats_by_flight", [])

        for flight_index, flight in enumerate(selected_flights):
            if flight_index == 0:
                segment_date = search_data.get("depart_date", "")
            elif search_data.get("trip_type") == "return":
                segment_date = search_data.get("return_date", "")
            else:
                multi_flights = search_data.get("multi_flights", [])
                segment_date = multi_flights[flight_index].get("depart_date", "") if flight_index < len(multi_flights) else ""

            segment_seats = selected_seats_by_flight[flight_index] if flight_index < len(selected_seats_by_flight) else []

            conn.execute("""
                INSERT INTO booking_flights (
                    booking_id, flight_order, airline, flight_number,
                    departure_airport, departure_city, departure_code,
                    destination_airport, destination_city, destination_code,
                    flight_date, departure_time, arrival_time,
                    ticket_class, seat
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                booking_id,
                flight_index + 1,
                flight["airline"],
                flight.get("flight_number", ""),
                flight["from"],
                flight["from_city"],
                flight["from_code"],
                flight["to"],
                flight["to_city"],
                flight["to_code"],
                segment_date,
                flight["departure_time"],
                flight["arrival_time"],
                flight["class"],
                ", ".join(segment_seats)
            ))

        for index, passenger in enumerate(passengers):
            extra = passenger_extras[index] if index < len(passenger_extras) else {}

            passenger_seats = []
            for flight_index in range(len(selected_flights)):
                seat_index = index + (flight_index * passenger_count)
                if seat_index < len(selected_seats):
                    passenger_seats.append(selected_seats[seat_index])

            passenger_seat_text = ", ".join(passenger_seats)

            conn.execute("""
                INSERT INTO passengers (
                    booking_id, first_name, last_name, email, phone, passport_number,
                    assistance_required, assistance_options, other_assistance,
                    baggage, meal_choice, baggage_price, seat
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                booking_id,
                passenger["first_name"],
                passenger["last_name"],
                passenger["email"],
                passenger["phone"],
                passenger["passport_number"],
                passenger.get("assistance_required", ""),
                ", ".join(passenger.get("assistance_options", [])),
                passenger.get("other_assistance", ""),
                extra.get("baggage", "No checked bag"),
                extra.get("meal_choice", "No Meal"),
                extra.get("baggage_price", 0),
                passenger_seat_text
            ))

        conn.commit()
        conn.close()

        session["booking_reference"] = booking_reference
        session["points_earned"] = points_earned
        session["confirmed_booking_id"] = booking_id

        return redirect(url_for("confirmation"))

    return render_payment()

@app.route("/confirmation")
def confirmation():
    selected_flight = session.get("selected_flight")
    selected_flights = session.get("selected_flights", [selected_flight])
    passengers = session.get("passenger_data")
    selected_seats = session.get("selected_seats")
    booking_reference = session.get("booking_reference")
    points_earned = session.get("points_earned", 0)

    if not selected_flight or not passengers or not booking_reference:
        flash("No booking confirmation found.", "error")
        return redirect(url_for("home"))

    conn = get_db_connection()
    booking = conn.execute("SELECT id FROM bookings WHERE booking_reference = ?", (booking_reference,)).fetchone()
    conn.close()
    booking_id = booking["id"] if booking else None

    return render_template(
        "confirmation.html",
        flight=selected_flight,
        passenger=passengers[0],
        passengers=passengers,
        selected_seat=", ".join(selected_seats or []),
        selected_seats=selected_seats or [],
        booking_reference=booking_reference,
        benefits=CLASS_BENEFITS.get(selected_flight["class"], {}),
        points_earned=points_earned,
        extras=session.get("extras", {}),
        search_data=session.get("search_data", {}),
        selected_flights = session.get("selected_flights", [selected_flight]),
        booking_id=booking_id
    )

@app.route("/bookings")
def bookings():
    if not session.get("user_id"):
        session["post_login_redirect"] = url_for("bookings")
        flash("Please log in to view and manage your bookings.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()

    flight_bookings = conn.execute("""
        SELECT * FROM bookings
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    hotel_bookings = conn.execute("""
        SELECT * FROM hotel_bookings
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    total_points = conn.execute("""
        SELECT COALESCE(SUM(points_earned), 0) AS total
        FROM bookings
        WHERE user_id = ?
    """, (session["user_id"],)).fetchone()["total"]

    passenger_rows = conn.execute("""
        SELECT *
        FROM passengers
        WHERE booking_id IN (
            SELECT id FROM bookings WHERE user_id = ?
        )
        ORDER BY id
    """, (session["user_id"],)).fetchall()

    flight_segment_rows = conn.execute("""
        SELECT booking_flights.*
        FROM booking_flights
        JOIN bookings ON booking_flights.booking_id = bookings.id
        WHERE bookings.user_id = ?
        ORDER BY booking_flights.booking_id, booking_flights.flight_order
    """, (session["user_id"],)).fetchall()

    conn.close()

    enriched_bookings = []

    for row in flight_bookings:
        booking_dict = enrich_booking_for_display(row)

        booking_passengers = [
            dict(passenger)
            for passenger in passenger_rows
            if passenger["booking_id"] == row["id"]
        ]

        flight_segments = [
            dict(segment)
            for segment in flight_segment_rows
            if segment["booking_id"] == row["id"]
        ]

        if not flight_segments:
            flight_segments = [{
                "airline": booking_dict["airline"],
                "departure_airport": booking_dict["departure_airport"],
                "departure_city": booking_dict["departure_city"],
                "departure_code": booking_dict["departure_code"],
                "destination_airport": booking_dict["destination_airport"],
                "destination_city": booking_dict["destination_city"],
                "destination_code": booking_dict["destination_code"],
                "flight_date": booking_dict["flight_date"],
                "departure_time": booking_dict["departure_time"],
                "arrival_time": booking_dict["arrival_time"],
                "ticket_class": booking_dict["ticket_class"],
                "seat": booking_dict["seat"],
            }]

        for passenger in booking_passengers:
            passenger_class = passenger.get("ticket_class") or booking_dict["ticket_class"]
            passenger["available_upgrades"] = get_available_upgrades(passenger_class)

        booking_dict["flight_segments"] = flight_segments
        booking_dict["passengers"] = booking_passengers

        enriched_bookings.append(booking_dict)

    tier_info = get_tier_info(total_points)

    conn2 = get_db_connection()
    taxi_bookings = conn2.execute("""
        SELECT * FROM taxi_bookings WHERE user_id = ? ORDER BY id DESC
    """, (session["user_id"],)).fetchall()
    conn2.close()

    return render_template(
        "bookings.html",
        bookings=enriched_bookings,
        hotel_bookings=hotel_bookings,
        taxi_bookings=taxi_bookings,
        total_points=total_points,
        common_meal_options=COMMON_MEAL_OPTIONS,
        tier_info=tier_info,
        extra_prices=EXTRA_PRICES,
        today=date.today().isoformat(),
    )

@app.route("/update-passenger-meal/<int:passenger_id>", methods=["POST"])
def update_passenger_meal(passenger_id):
    if not session.get("user_id"):
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    new_meal = request.form.get("meal_choice", "").strip()

    conn = get_db_connection()
    passenger = conn.execute("""
        SELECT passengers.*
        FROM passengers
        JOIN bookings ON passengers.booking_id = bookings.id
        WHERE passengers.id = ? AND bookings.user_id = ?
    """, (passenger_id, session["user_id"])).fetchone()

    if not passenger:
        conn.close()
        flash("Passenger not found.", "error")
        return redirect(url_for("bookings"))

    conn.execute("""
        UPDATE passengers
        SET meal_choice = ?
        WHERE id = ?
    """, (new_meal, passenger_id))

    conn.commit()
    conn.close()

    flash("Meal updated for selected passenger.", "success")
    return redirect(url_for("bookings"))

@app.route("/update-passenger-extras/<int:passenger_id>", methods=["POST"])
def update_passenger_extras(passenger_id):
    if not session.get("user_id"):
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    baggage = request.form.get("baggage", "No checked bag")
    priority_boarding = 1 if request.form.get("priority_boarding") == "on" else 0
    wifi_package = 1 if request.form.get("wifi_package") == "on" else 0
    lounge_access = 1 if request.form.get("lounge_access") == "on" else 0

    baggage_price = 0
    if "1 checked bag" in baggage:
        baggage_price = 30
    elif "2 checked bags" in baggage:
        baggage_price = 60

    extras_price = (
        baggage_price
        + priority_boarding * EXTRA_PRICES["priority_boarding"]
        + wifi_package * EXTRA_PRICES["wifi_package"]
        + lounge_access * EXTRA_PRICES["lounge_access"]
    )

    conn = get_db_connection()

    passenger = conn.execute("""
        SELECT passengers.*, bookings.price
        FROM passengers
        JOIN bookings ON passengers.booking_id = bookings.id
        WHERE passengers.id = ? AND bookings.user_id = ?
    """, (passenger_id, session["user_id"])).fetchone()

    if not passenger:
        conn.close()
        flash("Passenger not found.", "error")
        return redirect(url_for("bookings"))

    old_extras_price = (
        float(passenger["baggage_price"] or 0)
        + int(passenger["priority_boarding"] or 0) * EXTRA_PRICES["priority_boarding"]
        + int(passenger["wifi_package"] or 0) * EXTRA_PRICES["wifi_package"]
        + int(passenger["lounge_access"] or 0) * EXTRA_PRICES["lounge_access"]
    )

    new_booking_price = float(passenger["price"]) - old_extras_price + extras_price
    new_points = calculate_points(new_booking_price)

    conn.execute("""
        UPDATE passengers
        SET baggage = ?,
            baggage_price = ?,
            priority_boarding = ?,
            wifi_package = ?,
            lounge_access = ?
        WHERE id = ?
    """, (
        baggage,
        baggage_price,
        priority_boarding,
        wifi_package,
        lounge_access,
        passenger_id
    ))

    conn.execute("""
        UPDATE bookings
        SET price = ?,
            points_earned = ?
        WHERE id = ?
    """, (
        new_booking_price,
        new_points,
        passenger["booking_id"]
    ))

    conn.commit()
    conn.close()

    flash("Extras updated for selected passenger.", "success")
    return redirect(url_for("bookings"))

@app.route("/upgrade-passenger/<int:passenger_id>", methods=["POST"])
def upgrade_passenger(passenger_id):
    if not session.get("user_id"):
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    new_class = request.form.get("new_class", "").strip()

    conn = get_db_connection()

    passenger = conn.execute("""
        SELECT passengers.*, bookings.ticket_class AS booking_ticket_class, bookings.price
        FROM passengers
        JOIN bookings ON passengers.booking_id = bookings.id
        WHERE passengers.id = ? AND bookings.user_id = ?
    """, (passenger_id, session["user_id"])).fetchone()

    if not passenger:
        conn.close()
        flash("Passenger not found.", "error")
        return redirect(url_for("bookings"))

    current_class = passenger["ticket_class"] or passenger["booking_ticket_class"]
    valid_upgrades = get_available_upgrades(current_class)

    if new_class not in valid_upgrades:
        conn.close()
        flash("That upgrade option is not available for this passenger.", "error")
        return redirect(url_for("bookings"))

    upgrade_cost = valid_upgrades[new_class]
    old_upgrade_cost = float(passenger["upgrade_cost"] or 0)

    booking = conn.execute("""
        SELECT * FROM bookings
        WHERE id = ?
    """, (passenger["booking_id"],)).fetchone()

    new_booking_price = float(booking["price"] or 0) - old_upgrade_cost + upgrade_cost
    new_points = calculate_points(new_booking_price)

    conn.execute("""
        UPDATE passengers
        SET ticket_class = ?,
            upgrade_cost = ?
        WHERE id = ?
    """, (
        new_class,
        upgrade_cost,
        passenger_id
    ))

    conn.execute("""
        UPDATE bookings
        SET price = ?,
            points_earned = ?,
            change_request = '',
            change_status = 'None'
        WHERE id = ?
    """, (
        new_booking_price,
        new_points,
        passenger["booking_id"]
    ))

    conn.commit()
    conn.close()

    flash(f"Passenger upgraded to {new_class}.", "success")
    return redirect(url_for("bookings"))


@app.route("/request-change/<int:booking_id>", methods=["POST"])
def request_change(booking_id):
    if not session.get("user_id"):
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    requested_departure = request.form.get("requested_departure", "").strip()
    requested_destination = request.form.get("requested_destination", "").strip()
    requested_date = request.form.get("requested_date", "").strip()
    request_reason = request.form.get("request_reason", "").strip()
    change_passenger_ids = request.form.getlist("change_passenger_ids")

    if not requested_departure or not requested_destination or not requested_date:
        flash("Please select a new departure airport, destination airport, and date.", "error")
        return redirect(url_for("bookings"))

    if not change_passenger_ids:
        flash("Please select at least one passenger to change.", "error")
        return redirect(url_for("bookings"))

    if requested_date < date.today().isoformat():
        flash("You cannot request a change to a date that has already passed.", "error")
        return redirect(url_for("bookings"))

    departure_airport = parse_airport_selection(requested_departure)
    destination_airport = parse_airport_selection(requested_destination)

    if not departure_airport:
        flash("Please select a valid departure airport from the suggestions.", "error")
        return redirect(url_for("bookings"))

    if not destination_airport:
        flash("Please select a valid destination airport from the suggestions.", "error")
        return redirect(url_for("bookings"))

    requested_route_summary = (
        f"{departure_airport['name']} ({departure_airport['code']}) "
        f"to {destination_airport['name']} ({destination_airport['code']})"
    )

    request_summary = (
        f"Requested Route: {requested_route_summary} | "
        f"Requested Date: {requested_date} | "
        f"Reason: {request_reason or 'No reason given'}"
    )

    conn = get_db_connection()

    booking = conn.execute("""
        SELECT * FROM bookings
        WHERE id = ? AND user_id = ?
    """, (booking_id, session["user_id"])).fetchone()

    if not booking:
        conn.close()
        flash("Booking not found.", "error")
        return redirect(url_for("bookings"))
    
    if booking["flight_status"] == "Cancelled" or booking["passenger_count"] <= 0:
        conn.close()
        flash("This booking is cancelled, so you cannot request changes.", "error")
        return redirect(url_for("bookings"))

    conn.execute("""
        UPDATE bookings
        SET change_request = ?,
            change_status = ?,
            requested_route = ?,
            requested_date = ?,
            requested_departure_airport = ?,
            requested_departure_city = ?,
            requested_departure_code = ?,
            requested_destination_airport = ?,
            requested_destination_city = ?,
            requested_destination_code = ?,
            requested_passenger_ids = ?
        WHERE id = ? AND user_id = ?
    """, (
        request_summary,
        "Pending",
        requested_route_summary,
        requested_date,
        departure_airport["name"],
        departure_airport["city"],
        departure_airport["code"],
        destination_airport["name"],
        destination_airport["city"],
        destination_airport["code"],
        ",".join(change_passenger_ids),
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

    if not booking:
        conn.close()
        flash("Boarding pass not found.", "error")
        return redirect(url_for("bookings"))

    if booking["flight_status"] == "Cancelled":
        conn.close()
        flash("This booking is cancelled, so no boarding pass is available.", "error")
        return redirect(url_for("bookings"))

    passengers = conn.execute("""
        SELECT * FROM passengers
        WHERE booking_id = ?
          AND status != 'Cancelled'
        ORDER BY id
    """, (booking_id,)).fetchall()

    flight_segments = conn.execute("""
        SELECT *
        FROM booking_flights
        WHERE booking_id = ?
        ORDER BY flight_order
    """, (booking_id,)).fetchall()

    flight_segments = [dict(seg) for seg in flight_segments]

    conn.close()

    if not passengers:
        flash("There are no active passengers for this booking.", "error")
        return redirect(url_for("bookings"))

    if not flight_segments:
        flight_segments = [{
            "airline": booking["airline"],
            "departure_airport": booking["departure_airport"],
            "departure_city": booking["departure_city"],
            "departure_code": booking["departure_code"],
            "destination_airport": booking["destination_airport"],
            "destination_city": booking["destination_city"],
            "destination_code": booking["destination_code"],
            "flight_date": booking["flight_date"],
            "departure_time": booking["departure_time"],
            "arrival_time": booking["arrival_time"],
            "ticket_class": booking["ticket_class"],
            "seat": booking["seat"],
            "flight_order": 1
        }]

    return render_template(
        "boarding_pass.html",
        booking=booking,
        passengers=passengers,
        flight_segments=flight_segments,
        flight_number=booking["booking_reference"],
        display_status=booking["flight_status"],
        t=get_translation()
    )

@app.route("/request-refund/<int:booking_id>", methods=["POST"])
def request_refund(booking_id):
    if not session.get("user_id"):
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    refund_reason = request.form.get("refund_reason", "").strip()
    refund_custom_reason = request.form.get("refund_custom_reason", "").strip()
    refund_passenger_ids = request.form.getlist("refund_passenger_ids")

    if not refund_passenger_ids:
        flash("Please select at least one passenger to refund.", "error")
        return redirect(url_for("bookings"))

    conn = get_db_connection()

    booking = conn.execute("""
        SELECT * FROM bookings
        WHERE id = ? AND user_id = ?
    """, (booking_id, session["user_id"])).fetchone()

    if not booking:
        conn.close()
        flash("Booking not found.", "error")
        return redirect(url_for("bookings"))

    passengers = conn.execute(f"""
        SELECT * FROM passengers
        WHERE booking_id = ?
        AND id IN ({",".join(["?"] * len(refund_passenger_ids))})
        AND status != 'Cancelled'
    """, [booking_id] + refund_passenger_ids).fetchall()

    if not passengers:
        conn.close()
        flash("No valid passengers selected for refund.", "error")
        return redirect(url_for("bookings"))

    active_passengers = conn.execute("""
        SELECT COUNT(*) AS total
        FROM passengers
        WHERE booking_id = ? AND status != 'Cancelled'
    """, (booking_id,)).fetchone()["total"]

    price_per_passenger = booking["price"] / active_passengers if active_passengers else 0
    estimated_refund = round(price_per_passenger * len(passengers), 2)

    conn.execute("""
        UPDATE bookings
        SET refund_reason = ?,
            refund_custom_reason = ?,
            refund_passengers = ?,
            refund_passenger_ids = ?,
            refund_status = 'Pending',
            refund_amount = ?,
            refund_processed = 0
        WHERE id = ? AND user_id = ?
    """, (
        refund_reason,
        refund_custom_reason,
        len(passengers),
        ",".join(refund_passenger_ids),
        estimated_refund,
        booking_id,
        session["user_id"]
    ))

    conn.commit()
    conn.close()

    flash("Refund request submitted.", "success")
    return redirect(url_for("bookings"))




@app.route("/cancel-passenger/<int:passenger_id>", methods=["POST"])
def cancel_passenger(passenger_id):
    if not session.get("user_id"):
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    passenger = conn.execute(
        """SELECT passengers.*, bookings.user_id FROM passengers
           JOIN bookings ON passengers.booking_id = bookings.id
           WHERE passengers.id = ?""",
        (passenger_id,)
    ).fetchone()

    if not passenger or passenger["user_id"] != session["user_id"]:
        flash("Passenger not found.", "error")
        conn.close()
        return redirect(url_for("bookings"))

    if passenger["status"] == "Cancelled":
        flash("This passenger is already cancelled.", "info")
        conn.close()
        return redirect(url_for("bookings"))

    # check cancel up to half policy
    booking_id = passenger["booking_id"]
    all_passengers = conn.execute(
        "SELECT status FROM passengers WHERE booking_id = ?", (booking_id,)
    ).fetchall()

    total = len(all_passengers)
    already_cancelled = sum(1 for p in all_passengers if p["status"] == "Cancelled")
    max_allowed = total // 2

    if already_cancelled >= max_allowed:
        flash(f"You can only cancel up to half of your passengers ({max_allowed} out of {total}). Policy does not allow cancelling more.", "error")
        conn.close()
        return redirect(url_for("bookings"))

    conn.execute("UPDATE passengers SET status = 'Cancelled' WHERE id = ?", (passenger_id,))
    conn.commit()
    conn.close()

    flash(f"Passenger cancelled successfully.", "success")
    return redirect(url_for("bookings"))

@app.route("/track", methods=["GET", "POST"])
def track_flight():
    booking = None
    not_found = False

    if request.method == "POST":
        ref = request.form.get("booking_reference", "").strip().upper()
        conn = get_db_connection()
        booking = conn.execute(
            "SELECT * FROM bookings WHERE UPPER(booking_reference) = ?", (ref,)
        ).fetchone()
        conn.close()

        if not booking:
            not_found = True

    return render_template("flight_tracker.html", booking=booking, not_found=not_found, t=get_translation())


@app.route("/taxis", methods=["GET", "POST"])
def taxis():
    t = get_translation()
    results = None
    error = None
    booking = None
    ticket_class = None

    booking_id = request.args.get("booking_id")
    if booking_id:
        conn = get_db_connection()
        booking = conn.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
        conn.close()
        if booking:
            ticket_class = booking["ticket_class"]

    if request.method == "POST":
        pickup = request.form.get("pickup", "").strip()
        dropoff = request.form.get("dropoff", "").strip()
        transfer_type = request.form.get("transfer_type", "Standard Taxi")

        if not pickup or not dropoff:
            error = "Please enter both pickup and drop-off locations."
        else:
            import urllib.request as urllib_request
            import json
            import urllib.parse as urllib_parse

            api_key = "AIzaSyAw4YXog-zTq9rtPkXdQcyf2fw3r9fe3fU"
            url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={urllib_parse.quote(pickup)}&destinations={urllib_parse.quote(dropoff)}&key={api_key}"

            distance_km = None
            duration_text = ""
            try:
                req = urllib_request.urlopen(url)
                data = json.loads(req.read().decode())
                if data["status"] == "OK" and data["rows"][0]["elements"][0]["status"] == "OK":
                    distance_m = data["rows"][0]["elements"][0]["distance"]["value"]
                    duration_text = data["rows"][0]["elements"][0]["duration"]["text"]
                    distance_km = round(distance_m / 1000, 1)
                else:
                    error = f"Could not calculate distance. API status: {data['status']} - Element status: {data['rows'][0]['elements'][0]['status']}"
            except Exception as e:
                distance_km = 30.0
                duration_text = "Estimated ~45 mins"

            if distance_km:
                base_per_km = 1.5
                all_options = [
                    {"name": "Standard Taxi", "desc": "Comfortable sedan, fits up to 4 passengers", "price": round(distance_km * base_per_km + 5, 2), "icon": "🚕"},
                    {"name": "Minivan", "desc": "Spacious van, fits up to 7 passengers with luggage", "price": round(distance_km * base_per_km * 1.4 + 8, 2), "icon": "🚐"},
                    {"name": "Luxury Car", "desc": "Premium Mercedes S-Class, private transfer for up to 4", "price": round(distance_km * base_per_km * 2.5 + 20, 2), "icon": "🚘"},
                    {"name": "Meet & Greet + Luxury Transfer", "desc": "Met at the gate, fast track security, porter, Mercedes V-Class for up to 7", "price": round(distance_km * base_per_km * 3 + 60, 2), "icon": "⭐"}
                ]
                results = {"distance": distance_km, "duration": duration_text, "options": [o for o in all_options if o["name"] == transfer_type]}

            if results:
                session["taxi_results"] = results
                session["taxi_pickup"] = pickup
                session["taxi_dropoff"] = dropoff
                session["taxi_class"] = transfer_type
                return redirect(url_for("taxi_results"))

    return render_template("taxis.html",
        error=error,
        booking=booking,
        ticket_class=ticket_class,
        t=t
    )


@app.route("/taxis/results")
def taxi_results():
    t = get_translation()
    results = session.get("taxi_results")
    pickup = session.get("taxi_pickup")
    dropoff = session.get("taxi_dropoff")
    ticket_class = session.get("taxi_class", "Economy")

    if not results:
        return redirect(url_for("taxis"))

    return render_template("taxi_results.html",
        results=results,
        pickup=pickup,
        dropoff=dropoff,
        ticket_class=ticket_class,
        logged_in=bool(session.get("user_id")),
        t=t
    )


@app.route("/taxi/details", methods=["GET", "POST"])
def taxi_details():
    t = get_translation()
    if not session.get("user_id"):
        session["post_login_redirect"] = url_for("taxi_details")
        flash("Please log in to book a transfer.", "error")
        return redirect(url_for("login"))
 
    results = session.get("taxi_results")
    if not results or not results.get("options"):
        return redirect(url_for("taxis"))
 
    option = results["options"][0]
 
    conn = get_db_connection()
    existing_booking = conn.execute("""
        SELECT * FROM bookings WHERE user_id = ? ORDER BY id DESC LIMIT 1
    """, (session["user_id"],)).fetchone()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
 
    prefill = {}
    if existing_booking:
        prefill["first_name"] = existing_booking["first_name"]
        prefill["last_name"] = existing_booking["last_name"]
        prefill["phone"] = existing_booking["phone"]
        prefill["email"] = existing_booking["email"]
    elif user:
        name_parts = user["full_name"].split(" ", 1)
        prefill["first_name"] = name_parts[0]
        prefill["last_name"] = name_parts[1] if len(name_parts) > 1 else ""
        prefill["email"] = user["email"]
        prefill["phone"] = ""
 
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        phone = request.form.get("phone", "").strip()
        alt_phone = request.form.get("alt_phone", "").strip()
        email = request.form.get("email", "").strip()
 
        if not first_name or not last_name or not phone or not email:
            flash("Please fill in all required fields.", "error")
            return render_template("taxi_details.html", prefill=request.form, option=option, results=results, t=t)
 
        session["taxi_passenger"] = {
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "alt_phone": alt_phone,
            "email": email
        }
        return redirect(url_for("taxi_payment"))
 
    return render_template("taxi_details.html", prefill=prefill, option=option, results=results, t=t)


@app.route("/taxi/payment", methods=["GET", "POST"])
def taxi_payment():
    t = get_translation()

    if not session.get("user_id"):
        session["post_login_redirect"] = url_for("taxi_payment")
        flash("Please log in to complete your booking.", "error")
        return redirect(url_for("login"))

    results = session.get("taxi_results")
    passenger = session.get("taxi_passenger")
    pickup = session.get("taxi_pickup")
    dropoff = session.get("taxi_dropoff")

    if not results or not passenger or not pickup or not dropoff:
        return redirect(url_for("taxis"))

    option = results["options"][0]
    total_price = float(option["price"])

    conn = get_db_connection()
    available_points = conn.execute("""
        SELECT COALESCE(SUM(points_earned), 0) AS total_points
        FROM bookings
        WHERE user_id = ?
    """, (session["user_id"],)).fetchone()["total_points"]
    conn.close()

    max_discount = min(available_points // 100, int(total_price))

    point_options = []
    for discount in range(5, max_discount + 1, 5):
        point_options.append({
            "points": discount * 100,
            "discount": discount
        })

    def render_taxi_payment(points_used=0, points_discount=0, final_price=None):
        return render_template(
            "taxi_payment.html",
            option=option,
            pickup=pickup,
            dropoff=dropoff,
            passenger=passenger,
            total_price=total_price,
            final_price=final_price if final_price is not None else total_price,
            available_points=available_points,
            point_options=point_options,
            points_used=points_used,
            points_discount=points_discount,
            results=results,
            current_month=datetime.now().strftime("%Y-%m"),
            selected_currency=session.get("currency", "GBP"),
            t=t
        )

    if request.method == "POST":
        points_used = int(request.form.get("points_to_use", 0) or 0)

        if points_used < 0:
            points_used = 0

        if points_used > available_points:
            flash("You do not have enough points for that discount.", "error")
            return render_taxi_payment()

        points_discount = points_used / 100
        final_price = max(0, total_price - points_discount)

        card_name = request.form.get("card_name", "").strip()
        card_number = request.form.get("card_number", "").strip()
        expiry_date = request.form.get("expiry_date", "").strip()
        cvv = request.form.get("cvv", "").strip()

        if not request.form.get("accept_terms"):
            flash("You must accept the Terms & Conditions before completing your booking.", "error")
            return render_taxi_payment(points_used, points_discount, final_price)

        if not all([card_name, card_number, expiry_date, cvv]):
            flash("Please fill in all payment fields.", "error")
            return render_taxi_payment(points_used, points_discount, final_price)

        if not re.match(r"^[A-Za-z\s'-]+$", card_name):
            flash("Name on card must only contain letters.", "error")
            return render_taxi_payment(points_used, points_discount, final_price)

        if not card_number.isdigit() or len(card_number) != 16:
            flash("Card number must be exactly 16 digits.", "error")
            return render_taxi_payment(points_used, points_discount, final_price)

        if not cvv.isdigit() or len(cvv) not in [3, 4]:
            flash("CVV must be 3 or 4 digits.", "error")
            return render_taxi_payment(points_used, points_discount, final_price)

        booking_reference = generate_booking_reference()

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO taxi_bookings (
                user_id, booking_reference, first_name, last_name, phone, alt_phone,
                email, transfer_type, pickup, dropoff, distance_km, duration,
                price, booking_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            booking_reference,
            passenger["first_name"],
            passenger["last_name"],
            passenger["phone"],
            passenger.get("alt_phone", ""),
            passenger["email"],
            session.get("taxi_class", option["name"]),
            pickup,
            dropoff,
            results["distance"],
            results["duration"],
            final_price,
            date.today().isoformat(),
            "Confirmed"
        ))
        conn.commit()
        conn.close()

        session["taxi_booking_reference"] = booking_reference
        session["taxi_booking_price"] = final_price

        return redirect(url_for("taxi_confirmation"))

    return render_taxi_payment()

@app.route("/taxi/confirmation")
def taxi_confirmation():
    t = get_translation()
    booking_reference = session.get("taxi_booking_reference")
    price = session.get("taxi_booking_price")
    pickup = session.get("taxi_pickup")
    dropoff = session.get("taxi_dropoff")
    transfer_type = session.get("taxi_class")
    passenger = session.get("taxi_passenger")

    if not booking_reference:
        return redirect(url_for("bookings"))

    return render_template("taxi_confirmation.html",
        booking_reference=booking_reference,
        price=price,
        pickup=pickup,
        dropoff=dropoff,
        transfer_type=transfer_type,
        passenger=passenger,
        t=t
    )


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

    hotel_rows = conn.execute("""
        SELECT hotel_bookings.*, users.full_name AS account_name
        FROM hotel_bookings
        JOIN users ON hotel_bookings.user_id = users.id
        ORDER BY hotel_bookings.id DESC
    """).fetchall()

    conn.close()

    bookings = [enrich_booking_for_display(row) for row in rows]

    return render_template(
        "admin.html",
        bookings=bookings,
        hotel_bookings=hotel_rows,
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
        passenger_ids = [
            pid.strip()
            for pid in (booking["requested_passenger_ids"] or "").split(",")
            if pid.strip()
        ]

        if passenger_ids:
            conn.execute(f"""
                UPDATE passengers
                SET status = 'Changed',
                    changed_departure_airport = ?,
                    changed_departure_city = ?,
                    changed_departure_code = ?,
                    changed_destination_airport = ?,
                    changed_destination_city = ?,
                    changed_destination_code = ?,
                    changed_flight_date = ?
                WHERE booking_id = ?
                AND id IN ({",".join(["?"] * len(passenger_ids))})
                AND status != 'Cancelled'
            """, [
                booking["requested_departure_airport"] or booking["departure_airport"],
                booking["requested_departure_city"] or booking["departure_city"],
                booking["requested_departure_code"] or booking["departure_code"],
                booking["requested_destination_airport"] or booking["destination_airport"],
                booking["requested_destination_city"] or booking["destination_city"],
                booking["requested_destination_code"] or booking["destination_code"],
                booking["requested_date"] or booking["flight_date"],
                booking_id,
                *passenger_ids
            ])

        conn.execute("""
            UPDATE bookings
            SET change_status = ?
            WHERE id = ?
        """, (new_status, booking_id))

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

@app.route("/admin/update-refund-status/<int:booking_id>", methods=["POST"])
def admin_update_refund_status(booking_id):
    if not is_admin():
        flash("Admin access only.", "error")
        return redirect(url_for("home"))

    new_status = request.form.get("refund_status", "").strip()

    if new_status not in ["Pending", "Approved", "Rejected"]:
        flash("Invalid refund status.", "error")
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

    if new_status == "Approved":
        refund_ids = [
            passenger_id.strip()
            for passenger_id in (booking["refund_passenger_ids"] or "").split(",")
            if passenger_id.strip()
        ]

        if refund_ids:
            conn.execute(f"""
                UPDATE passengers
                SET status = 'Cancelled'
                WHERE booking_id = ?
                AND id IN ({",".join(["?"] * len(refund_ids))})
            """, [booking_id] + refund_ids)

        active_count = conn.execute("""
            SELECT COUNT(*) AS total
            FROM passengers
            WHERE booking_id = ? AND status != 'Cancelled'
        """, (booking_id,)).fetchone()["total"]

        new_price = max(0, round(booking["price"] - booking["refund_amount"], 2))
        new_points = calculate_points(new_price)

        new_flight_status = "Cancelled" if active_count == 0 else booking["flight_status"]

        conn.execute("""
            UPDATE bookings
            SET refund_status = ?,
                refund_processed = 1,
                passenger_count = ?,
                price = ?,
                points_earned = ?,
                flight_status = ?,
                refund_passenger_ids = ''
            WHERE id = ?
        """, (
            new_status,
            active_count,
            new_price,
            new_points,
            new_flight_status,
            booking_id
        ))

    elif new_status == "Rejected":
        conn.execute("""
            UPDATE bookings
            SET refund_status = ?,
                refund_passengers = 0,
                refund_amount = 0,
                refund_passenger_ids = ''
            WHERE id = ?
        """, (new_status, booking_id))

    else:
        conn.execute("""
            UPDATE bookings
            SET refund_status = ?
            WHERE id = ?
        """, (new_status, booking_id))

    conn.commit()
    conn.close()

    flash("Refund status updated.", "success")
    return redirect(url_for("admin_dashboard"))

    conn = get_db_connection()
    conn.execute("""
        UPDATE bookings
        SET refund_status = ?
        WHERE id = ?
    """, (status, booking_id))

    conn.commit()
    conn.close()

    flash("Refund status updated.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/hotels")
def hotels():
    today = date.today().isoformat()
    return render_template("hotels.html", today=today, prefill=None)

@app.route("/hotel_search")
@app.route("/hotels/search")
def hotel_search():
    destination = request.args.get("destination", "").strip()
    check_in = request.args.get("check_in", "")
    check_out = request.args.get("check_out", "")
    guests = request.args.get("guests", 1, type=int)
    flight_booking_id = request.args.get("flight_booking_id", "")

    nights = 1
    if check_in and check_out:
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
            if check_out_date <= check_in_date:
                flash("Check out date must be at least one day after check in.", "error")
                return redirect(url_for("hotels"))
            nights = (check_out_date - check_in_date).days
        except:
            nights = 1

    search_params = {
        "destination": destination,
        "check_in": check_in,
        "check_out": check_out,
        "guests": guests,
        "flight_booking_id": flight_booking_id
    }

    try:
        results = get_real_hotels(destination, check_in, check_out, guests)
    except Exception as e:
        print("Hotel API error:", e)
        results = []

    session["last_hotels"] = results

    return render_template(
        "hotel_results.html",
        hotels=results,
        results=results,
        search_params=search_params,
        destination=destination,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        flight_booking_id=flight_booking_id,
        nights=nights,
        t=get_translation()
    )

def get_exchange_rates():
    global EXCHANGE_RATES, LAST_FETCH

    if time.time() - LAST_FETCH < CACHE_DURATION:
        return EXCHANGE_RATES

    try:
        response = requests.get("https://open.er-api.com/v6/latest/GBP")
        data = response.json()

        if data.get("result") == "success":
            EXCHANGE_RATES = data["rates"]
            LAST_FETCH = time.time()

    except Exception as e:
        print("Currency API failed:", e)

    return EXCHANGE_RATES


def convert_price(amount, currency):
    rates = get_exchange_rates()
    rate = rates.get(currency, 1)
    return round(amount * rate, 2)

def normalize_search_text(text):
    text = (text or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


CURRENCY_NAMES = {
    "GBP": "British Pound", "USD": "US Dollar", "EUR": "Euro", "TRY": "Turkish Lira", "AED": "UAE Dirham",
    "CAD": "Canadian Dollar", "AUD": "Australian Dollar", "NZD": "New Zealand Dollar", "JPY": "Japanese Yen",
    "CNY": "Chinese Yuan", "INR": "Indian Rupee", "IRR": "Iranian Rial", "RUB": "Russian Ruble",
    "KRW": "South Korean Won", "THB": "Thai Baht", "CHF": "Swiss Franc", "SEK": "Swedish Krona",
    "NOK": "Norwegian Krone", "DKK": "Danish Krone", "SAR": "Saudi Riyal", "QAR": "Qatari Riyal",
    "KWD": "Kuwaiti Dinar", "BHD": "Bahraini Dinar", "OMR": "Omani Rial", "ZAR": "South African Rand",
    "BRL": "Brazilian Real", "MXN": "Mexican Peso", "ARS": "Argentine Peso", "CLP": "Chilean Peso",
    "COP": "Colombian Peso", "EGP": "Egyptian Pound", "MAD": "Moroccan Dirham", "ILS": "Israeli New Shekel",
    "PKR": "Pakistani Rupee", "BDT": "Bangladeshi Taka", "IDR": "Indonesian Rupiah", "MYR": "Malaysian Ringgit",
    "SGD": "Singapore Dollar", "HKD": "Hong Kong Dollar", "TWD": "New Taiwan Dollar", "PHP": "Philippine Peso",
    "VND": "Vietnamese Dong", "PLN": "Polish Zloty", "CZK": "Czech Koruna", "HUF": "Hungarian Forint",
    "RON": "Romanian Leu", "BGN": "Bulgarian Lev", "UAH": "Ukrainian Hryvnia", "ISK": "Icelandic Krona",
    "NGN": "Nigerian Naira", "KES": "Kenyan Shilling", "GHS": "Ghanaian Cedi"
}

CURRENCY_SYMBOLS = {
    "GBP": "£", "USD": "$", "EUR": "€", "TRY": "₺", "AED": "د.إ", "CAD": "$", "AUD": "$", "NZD": "$",
    "JPY": "¥", "CNY": "¥", "INR": "₹", "IRR": "﷼", "RUB": "₽", "KRW": "₩", "THB": "฿",
    "CHF": "CHF", "SEK": "kr", "NOK": "kr", "DKK": "kr", "SAR": "﷼", "QAR": "﷼", "KWD": "د.ك",
    "BHD": ".د.ب", "OMR": "﷼", "ZAR": "R", "BRL": "R$", "MXN": "$", "ARS": "$", "CLP": "$",
    "COP": "$", "EGP": "E£", "MAD": "MAD", "ILS": "₪", "PKR": "₨", "BDT": "৳", "IDR": "Rp",
    "MYR": "RM", "SGD": "$", "HKD": "$", "TWD": "NT$", "PHP": "₱", "VND": "₫", "PLN": "zł",
    "CZK": "Kč", "HUF": "Ft", "RON": "lei", "BGN": "лв", "UAH": "₴", "NGN": "₦", "KES": "KSh", "GHS": "₵"
}

CURRENCY_EXTRA_ALIASES = {
    "GBP": ["uk", "britain", "great britain", "united kingdom", "england", "scotland", "wales", "pound", "sterling"],
    "USD": ["usa", "us", "united states", "america", "american", "dollar"],
    "EUR": ["europe", "european union", "eurozone", "euro"],
    "TRY": ["turkey", "turkiye", "türkiye", "turkish", "lira"],
    "AED": ["uae", "united arab emirates", "emirates", "emirati", "dirham", "dubai", "abu dhabi"],
    "CAD": ["canada", "canadian"], "AUD": ["australia", "australian", "aus"], "NZD": ["new zealand", "kiwi"],
    "JPY": ["japan", "japanese", "yen"], "CNY": ["china", "chinese", "yuan", "renminbi"],
    "INR": ["india", "indian", "rupee"], "IRR": ["iran", "iranian", "rial"],
    "SAR": ["saudi", "saudi arabia", "riyal"], "QAR": ["qatar", "qatari", "riyal"],
    "KWD": ["kuwait", "kuwaiti", "dinar"], "BHD": ["bahrain", "bahraini", "dinar"], "OMR": ["oman", "omani", "rial"],
    "KRW": ["korea", "south korea", "korean", "won"], "THB": ["thailand", "thai", "baht"],
    "CHF": ["switzerland", "swiss", "franc"], "ZAR": ["south africa", "south african", "rand"],
    "BRL": ["brazil", "brazilian", "real"], "MXN": ["mexico", "mexican", "peso"],
    "ARS": ["argentina", "argentine", "peso"], "CLP": ["chile", "chilean", "peso"], "COP": ["colombia", "colombian", "peso"],
    "EGP": ["egypt", "egyptian", "pound"], "MAD": ["morocco", "moroccan", "dirham"], "ILS": ["israel", "israeli", "shekel"],
    "PKR": ["pakistan", "pakistani", "rupee"], "BDT": ["bangladesh", "bangladeshi", "taka"],
    "IDR": ["indonesia", "indonesian", "rupiah"], "MYR": ["malaysia", "malaysian", "ringgit"],
    "SGD": ["singapore", "singaporean"], "HKD": ["hong kong", "hongkong"], "TWD": ["taiwan", "taiwanese"],
    "PHP": ["philippines", "philippine", "filipino", "peso"], "VND": ["vietnam", "vietnamese", "dong"],
    "PLN": ["poland", "polish", "zloty"], "CZK": ["czech", "czechia", "czech republic", "koruna"],
    "HUF": ["hungary", "hungarian", "forint"], "RON": ["romania", "romanian", "leu"],
    "BGN": ["bulgaria", "bulgarian", "lev"], "UAH": ["ukraine", "ukrainian", "hryvnia"],
    "ISK": ["iceland", "icelandic", "krona"], "NGN": ["nigeria", "nigerian", "naira"],
    "KES": ["kenya", "kenyan", "shilling"], "GHS": ["ghana", "ghanaian", "cedi"]
}


def get_currency_display_name(code):
    return CURRENCY_NAMES.get(code, code)


def get_currency_symbol_for_code(code):
    return CURRENCY_SYMBOLS.get(code, "")


def build_currency_metadata():
    rates = get_exchange_rates()
    available_currencies = []
    for code in sorted(rates.keys()):
        name = get_currency_display_name(code)
        symbol = get_currency_symbol_for_code(code)
        aliases = set()
        aliases.add(normalize_search_text(code))
        aliases.add(normalize_search_text(name))
        for token in normalize_search_text(name).split():
            aliases.add(token)
        for alias in CURRENCY_EXTRA_ALIASES.get(code, []):
            aliases.add(normalize_search_text(alias))
            for token in normalize_search_text(alias).split():
                aliases.add(token)
        if symbol:
            aliases.add(normalize_search_text(symbol))
        available_currencies.append({
            "code": code,
            "name": name,
            "symbol": symbol,
            "aliases": sorted(a for a in aliases if a)
        })
    return available_currencies

@app.context_processor
def inject_currency():
    return {
        "selected_currency": session.get("currency", "GBP"),
        "convert_price": convert_price,
        "available_currencies": build_currency_metadata(),
        "t": get_translation()
    }
@app.context_processor
def inject_translations():
    return dict(t=get_translation())
@app.route("/set-language/<lang>")
def set_language(lang):
    allowed_languages = ["en", "fr", "ar"]

    if lang in allowed_languages:
        session["lang"] = lang
    else:
        session["lang"] = "en"

    return redirect(request.referrer or url_for("home"))

@app.route("/set-currency", methods=["POST"])
def set_currency():
    currency = request.form.get("currency", "GBP").upper()

    rates = get_exchange_rates()
    if currency in rates:
        session["currency"] = currency
    else:
        session["currency"] = "GBP"

    next_url = request.form.get("next_url", "").strip()

    if next_url:
        return redirect(next_url)

    return redirect(url_for("home"))

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/hotels/book/<int:hotel_id>", methods=["GET", "POST"])
def hotel_book(hotel_id):
    if not session.get("user_id"):
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    hotel = find_hotel_by_id(hotel_id)

    if not hotel:
        flash("Hotel not found.", "error")
        return redirect(url_for("hotels"))

    booking_details = {
        "check_in": request.args.get("check_in", ""),
        "check_out": request.args.get("check_out", ""),
        "guests": request.args.get("guests", "1"),
        "flight_booking_id": request.args.get("flight_booking_id", "")
    }

    try:
        check_in_date = datetime.strptime(booking_details["check_in"], "%Y-%m-%d")
        check_out_date = datetime.strptime(booking_details["check_out"], "%Y-%m-%d")
        nights = max(1, (check_out_date - check_in_date).days)
    except:
        nights = 1

    base_price = float(hotel.get("total_price", 0))

    if request.method == "POST":
        room_type = request.form.get("room_type", "Standard")
        total_price = float(request.form.get("total_price", base_price))

        session["pending_hotel_booking"] = {
            "hotel_name": hotel.get("name", ""),
            "hotel_address": hotel.get("address", ""),
            "hotel_city": hotel.get("city", ""),
            "hotel_country": hotel.get("country", ""),
            "check_in": booking_details["check_in"],
            "check_out": booking_details["check_out"],
            "guests": booking_details["guests"],
            "room_type": room_type,
            "total_price": total_price,
            "flight_booking_id": booking_details["flight_booking_id"]
        }

        return redirect(url_for("hotel_details"))

    return render_template(
        "hotel_booking.html",
        hotel=hotel,
        booking_details=booking_details,
        nights=nights,
        total_price=base_price,
        selected_currency=session.get("currency", "GBP"),
        t=get_translation()
    )

@app.route("/hotel-details", methods=["GET", "POST"])
def hotel_details():
    t = get_translation()

    if not session.get("user_id"):
        session["post_login_redirect"] = url_for("hotel_details")
        flash("Please log in to enter guest details.", "error")
        return redirect(url_for("login"))

    booking = session.get("pending_hotel_booking")

    if not booking:
        flash("Please choose a hotel first.", "error")
        return redirect(url_for("hotels"))

    guest_count = int(booking.get("guests", 1) or 1)
    guest_count = max(1, guest_count)

    if request.method == "POST":
        guests = []

        for i in range(1, guest_count + 1):
            guest = {
                "first_name": request.form.get(f"first_name_{i}", "").strip(),
                "last_name": request.form.get(f"last_name_{i}", "").strip(),
                "email": request.form.get(f"email_{i}", "").strip(),
                "phone": request.form.get(f"phone_{i}", "").strip(),
                "special_requests": request.form.get(f"special_requests_{i}", "").strip()
            }

            if not guest["first_name"] or not guest["last_name"] or not guest["email"] or not guest["phone"]:
                flash(f"Please fill in all required details for guest {i}.", "error")
                return render_template(
                    "hotel_details.html",
                    booking=booking,
                    guest_count=guest_count,
                    selected_currency=session.get("currency", "GBP"),
                    t=t
                )

            if not re.match(r"^[A-Za-zÀ-ÿ\s'-]+$", guest["first_name"]):
                flash(f"Guest {i} first name must only contain letters.", "error")
                return render_template(
                    "hotel_details.html",
                    booking=booking,
                    guest_count=guest_count,
                    selected_currency=session.get("currency", "GBP"),
                    t=t
                )

            if not re.match(r"^[A-Za-zÀ-ÿ\s'-]+$", guest["last_name"]):
                flash(f"Guest {i} last name must only contain letters.", "error")
                return render_template(
                    "hotel_details.html",
                    booking=booking,
                    guest_count=guest_count,
                    selected_currency=session.get("currency", "GBP"),
                    t=t
                )

            if not re.match(r"^0[0-9]{8,14}$", guest["phone"]):
                flash(f"Guest {i} phone number must start with 0 and contain 9 to 15 digits.", "error")
                return render_template(
                    "hotel_details.html",
                    booking=booking,
                    guest_count=guest_count,
                    selected_currency=session.get("currency", "GBP"),
                    t=t
                )

            guests.append(guest)

        session["pending_hotel_guests"] = guests
        return redirect(url_for("hotel_payment"))

    return render_template(
        "hotel_details.html",
        booking=booking,
        guest_count=guest_count,
        selected_currency=session.get("currency", "GBP"),
        t=t
    )

@app.route("/hotel-payment", methods=["GET", "POST"])
def hotel_payment():
    t = get_translation()

    if not session.get("user_id"):
        session["post_login_redirect"] = url_for("hotel_payment")
        flash("Please log in to complete your hotel booking.", "error")
        return redirect(url_for("login"))

    booking = session.get("pending_hotel_booking")
    hotel_guests = session.get("pending_hotel_guests")
    
    if not booking:
        flash("Please choose a hotel first.", "error")
        return redirect(url_for("hotels"))

    if not hotel_guests:
        flash("Please enter guest details first.", "error")
        return redirect(url_for("hotel_details"))

    total_price = float(booking.get("total_price", 0))

    conn = get_db_connection()
    available_points = conn.execute("""
        SELECT COALESCE(SUM(points_earned), 0) AS total_points
        FROM bookings
        WHERE user_id = ?
    """, (session["user_id"],)).fetchone()["total_points"]
    conn.close()

    max_discount = min(available_points // 100, int(total_price))

    point_options = []
    for discount in range(5, max_discount + 1, 5):
        point_options.append({
            "points": discount * 100,
            "discount": discount
        })

    def render_hotel_payment(points_used=0, points_discount=0, final_price=None):
        return render_template(
            "hotel_payment.html",
            booking=booking,
            hotel_guests=hotel_guests,
            total_price=total_price,
            final_price=final_price if final_price is not None else total_price,
            available_points=available_points,
            point_options=point_options,
            points_used=points_used,
            points_discount=points_discount,
            current_month=datetime.now().strftime("%Y-%m"),
            selected_currency=session.get("currency", "GBP"),
            t=t
        )

    if request.method == "POST":
        points_used = int(request.form.get("points_to_use", 0) or 0)

        if points_used < 0:
            points_used = 0

        if points_used > available_points:
            flash("You do not have enough points for that discount.", "error")
            return render_hotel_payment()

        points_discount = points_used / 100
        final_price = max(0, total_price - points_discount)

        card_name = request.form.get("card_name", "").strip()
        card_number = request.form.get("card_number", "").strip()
        expiry_date = request.form.get("expiry_date", "").strip()
        cvv = request.form.get("cvv", "").strip()

        if not request.form.get("accept_terms"):
            flash("You must accept the Terms & Conditions before completing your booking.", "error")
            return render_hotel_payment(points_used, points_discount, final_price)

        if not all([card_name, card_number, expiry_date, cvv]):
            flash("Please fill in all payment fields.", "error")
            return render_hotel_payment(points_used, points_discount, final_price)

        if not re.match(r"^[A-Za-z\s'-]+$", card_name):
            flash("Name on card must only contain letters.", "error")
            return render_hotel_payment(points_used, points_discount, final_price)

        if not card_number.isdigit() or len(card_number) != 16:
            flash("Card number must be exactly 16 digits.", "error")
            return render_hotel_payment(points_used, points_discount, final_price)

        if not cvv.isdigit() or len(cvv) not in [3, 4]:
            flash("CVV must be 3 or 4 digits.", "error")
            return render_hotel_payment(points_used, points_discount, final_price)

        booking_reference = generate_booking_reference()

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO hotel_bookings (
                user_id,
                hotel_name,
                hotel_city,
                hotel_country,
                check_in,
                check_out,
                guests,
                room_type,
                total_price,
                booking_reference,
                status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            booking["hotel_name"],
            booking["hotel_city"],
            booking["hotel_country"],
            booking["check_in"],
            booking["check_out"],
            int(booking["guests"]),
            booking["room_type"],
            final_price,
            booking_reference,
            "CONFIRMED"
        ))
        conn.commit()
        conn.close()

        session["hotel_confirmed_booking"] = {
            **booking,
            "hotel_guests": hotel_guests,
            "booking_reference": booking_reference,
            "total_price": final_price,
            "status": "CONFIRMED"
        }

        session.pop("pending_hotel_booking", None)
        session.pop("pending_hotel_guests", None)

        return redirect(url_for("hotel_confirmation"))

    return render_hotel_payment()

@app.route("/hotel-confirmation")
def hotel_confirmation():
    if not session.get("user_id"):
        flash("Please log in to view your hotel confirmation.", "error")
        return redirect(url_for("login"))

    booking = session.get("hotel_confirmed_booking")

    if not booking:
        flash("No hotel booking found.", "error")
        return redirect(url_for("hotels"))

    return render_template(
        "hotel_confirmation.html",
        booking=booking,
        selected_currency=session.get("currency", "GBP"),
        t=get_translation()
    )

@app.route("/request-hotel-refund/<int:hotel_booking_id>", methods=["POST"])
def request_hotel_refund(hotel_booking_id):
    if not session.get("user_id"):
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    refund_reason = request.form.get("refund_reason", "").strip()
    refund_custom_reason = request.form.get("refund_custom_reason", "").strip()

    if refund_reason == "Other" and not refund_custom_reason:
        flash("Please explain your refund reason.", "error")
        return redirect(url_for("bookings"))

    conn = get_db_connection()

    hotel_booking = conn.execute("""
        SELECT *
        FROM hotel_bookings
        WHERE id = ? AND user_id = ?
    """, (hotel_booking_id, session["user_id"])).fetchone()

    if not hotel_booking:
        conn.close()
        flash("Hotel booking not found.", "error")
        return redirect(url_for("bookings"))

    if hotel_booking["refund_status"] == "Pending":
        conn.close()
        flash("A refund request is already pending for this hotel booking.", "error")
        return redirect(url_for("bookings"))

    conn.execute("""
        UPDATE hotel_bookings
        SET refund_reason = ?,
            refund_custom_reason = ?,
            refund_status = 'Pending',
            refund_amount = ?
        WHERE id = ? AND user_id = ?
    """, (
        refund_reason,
        refund_custom_reason,
        hotel_booking["total_price"],
        hotel_booking_id,
        session["user_id"]
    ))

    conn.commit()
    conn.close()

    flash("Hotel refund request submitted successfully.", "success")
    return redirect(url_for("bookings"))

@app.route("/request-hotel-change/<int:hotel_booking_id>", methods=["POST"])
def request_hotel_change(hotel_booking_id):
    if not session.get("user_id"):
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    requested_check_in = request.form.get("requested_check_in", "").strip()
    requested_check_out = request.form.get("requested_check_out", "").strip()
    change_reason = request.form.get("change_reason", "").strip()

    if not requested_check_in or not requested_check_out:
        flash("Please enter both new hotel dates.", "error")
        return redirect(url_for("bookings"))

    if requested_check_out <= requested_check_in:
        flash("Check out date must be after check in date.", "error")
        return redirect(url_for("bookings"))

    conn = get_db_connection()

    hotel_booking = conn.execute("""
        SELECT *
        FROM hotel_bookings
        WHERE id = ? AND user_id = ?
    """, (hotel_booking_id, session["user_id"])).fetchone()

    if not hotel_booking:
        conn.close()
        flash("Hotel booking not found.", "error")
        return redirect(url_for("bookings"))

    conn.execute("""
        UPDATE hotel_bookings
        SET requested_check_in = ?,
            requested_check_out = ?,
            change_reason = ?,
            change_status = 'Pending'
        WHERE id = ? AND user_id = ?
    """, (
        requested_check_in,
        requested_check_out,
        change_reason,
        hotel_booking_id,
        session["user_id"]
    ))

    conn.commit()
    conn.close()

    flash("Hotel date change request submitted.", "success")
    return redirect(url_for("bookings"))


@app.route("/admin/update-hotel-refund-status/<int:hotel_booking_id>", methods=["POST"])
def admin_update_hotel_refund_status(hotel_booking_id):
    if not is_admin():
        flash("Admin access only.", "error")
        return redirect(url_for("home"))

    new_status = request.form.get("refund_status", "").strip()

    if new_status not in ["Pending", "Approved", "Rejected"]:
        flash("Invalid hotel refund status.", "error")
        return redirect(url_for("admin_dashboard"))

    conn = get_db_connection()

    hotel_booking = conn.execute("""
        SELECT *
        FROM hotel_bookings
        WHERE id = ?
    """, (hotel_booking_id,)).fetchone()

    if not hotel_booking:
        conn.close()
        flash("Hotel booking not found.", "error")
        return redirect(url_for("admin_dashboard"))

    if new_status == "Approved":
        conn.execute("""
            UPDATE hotel_bookings
            SET refund_status = ?,
                refund_processed = 1,
                refund_amount = total_price,
                total_price = 0,
                status = 'CANCELLED'
            WHERE id = ?
        """, (new_status, hotel_booking_id))

    elif new_status == "Rejected":
        conn.execute("""
            UPDATE hotel_bookings
            SET refund_status = ?,
                refund_processed = 0,
                refund_amount = 0
            WHERE id = ?
        """, (new_status, hotel_booking_id))

    else:
        conn.execute("""
            UPDATE hotel_bookings
            SET refund_status = ?,
                refund_processed = 1,
                refund_amount = ?,
                status = 'CANCELLED',
                total_price = 0
            WHERE id = ?
        """, (
            new_status,
            hotel_booking["total_price"],
            hotel_booking_id
        ))

    conn.commit()
    conn.close()

    flash("Hotel refund status updated.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/update-hotel-change-status/<int:hotel_booking_id>", methods=["POST"])
def admin_update_hotel_change_status(hotel_booking_id):
    if not is_admin():
        flash("Admin access only.", "error")
        return redirect(url_for("home"))

    new_status = request.form.get("change_status", "").strip()

    if new_status not in ["Pending", "Approved", "Rejected"]:
        flash("Invalid hotel change status.", "error")
        return redirect(url_for("admin_dashboard"))

    conn = get_db_connection()

    hotel_booking = conn.execute("""
        SELECT *
        FROM hotel_bookings
        WHERE id = ?
    """, (hotel_booking_id,)).fetchone()

    if not hotel_booking:
        conn.close()
        flash("Hotel booking not found.", "error")
        return redirect(url_for("admin_dashboard"))

    if new_status == "Approved":
        from datetime import datetime

        requested_check_in = hotel_booking["requested_check_in"]
        requested_check_out = hotel_booking["requested_check_out"]

        try:
            check_in_date = datetime.strptime(requested_check_in, "%Y-%m-%d")
            check_out_date = datetime.strptime(requested_check_out, "%Y-%m-%d")
            new_nights = max(1, (check_out_date - check_in_date).days)
        except:
            new_nights = 1

        matching_hotel = next(
            (hotel for hotel in SAMPLE_HOTELS if hotel["name"] == hotel_booking["hotel_name"]),
            None
        )

        if matching_hotel:
            price_per_night = matching_hotel["price_per_night"]
        else:
            price_per_night = 120

        conn.execute("""
            UPDATE hotel_bookings
            SET check_in = ?,
                check_out = ?,
                total_price = ?,
                change_status = ?,
                requested_check_in = '',
                requested_check_out = '',
                change_reason = ''
            WHERE id = ?
        """, (
            requested_check_in,
            requested_check_out,
            new_total_price,
            new_status,
            hotel_booking_id
        ))

    elif new_status == "Rejected":
        conn.execute("""
            UPDATE hotel_bookings
            SET change_status = ?,
                requested_check_in = '',
                requested_check_out = '',
                change_reason = ''
            WHERE id = ?
        """, (new_status, hotel_booking_id))

    else:
        conn.execute("""
            UPDATE hotel_bookings
            SET change_status = ?
            WHERE id = ?
        """, (new_status, hotel_booking_id))

    conn.commit()
    conn.close()

    flash("Hotel change status updated.", "success")
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)