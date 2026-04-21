from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
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
import pycountry
from babel.numbers import get_territory_currencies

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
        "example_departure": "e.g. London or LHR",

        "return_trip": "Return",
        "one_way": "One Way",
        "multi_city": "Multi City",

        "popular_routes": "Popular routes",
        "explore_destinations": "Explore our most booked destinations",
        "choose_destination": "Choose a destination to fill your search instantly and start booking faster.",
        "uk": "United Kingdom",
        "usa": "United States",

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
        "departure": "Departure",
        "arrival": "Arrival",
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
    "example_departure": "ex: Londres ou LHR",

    "return_trip": "Aller-retour",
    "one_way": "Aller simple",
    "multi_city": "Multi-destinations",

    "popular_routes": "Routes populaires",
    "explore_destinations": "Découvrez nos destinations les plus réservées",
    "choose_destination": "Choisissez une destination pour remplir votre recherche plus rapidement.",
    "uk": "Royaume-Uni",
    "usa": "États-Unis",

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
    "example_departure": "مثال: لندن أو LHR",

    "return_trip": "ذهاب وعودة",
    "one_way": "ذهاب فقط",
    "multi_city": "مدن متعددة",

    "popular_routes": "الوجهات الشائعة",
    "explore_destinations": "اكتشف الوجهات الأكثر حجزًا",
    "choose_destination": "اختر وجهة لملء البحث بسرعة.",
    "uk": "المملكة المتحدة",
    "usa": "الولايات المتحدة",

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
}
}
def get_translation():
    lang = session.get("lang", "en")
    base = translations["en"].copy()
    selected = translations.get(lang, {})
    base.update(selected)
    return base

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

SAMPLE_FLIGHTS = [
    {
        "id": 1,
        "airline": "AirGo",
        "from": "London Heathrow",
        "from_city": "London",
        "from_code": "LHR",
        "airport_group": "London Airports",
        "to": "Paris Charles de Gaulle",
        "to_city": "Paris",
        "to_code": "CDG",
        "destination_group": "Paris Airports",
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
        "airport_group": "London Airports",
        "to": "Paris Orly",
        "to_city": "Paris",
        "to_code": "ORY",
        "destination_group": "Paris Airports",
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
        "airport_group": "London Airports",
        "to": "Dubai International",
        "to_city": "Dubai",
        "to_code": "DXB",
        "destination_group": "Dubai Airports",
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
        "airport_group": "Paris Airports",
        "to": "Dubai International",
        "to_city": "Dubai",
        "to_code": "DXB",
        "destination_group": "Dubai Airports",
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
        "airport_group": "Dubai Airports",
        "to": "London Heathrow",
        "to_city": "London",
        "to_code": "LHR",
        "destination_group": "London Airports",
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
        "airport_group": "London Airports",
        "to": "John F. Kennedy",
        "to_city": "New York",
        "to_code": "JFK",
        "destination_group": "New York Airports",
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


def get_seat_type_and_price(seat_code, row_number, seat_letter):
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
                seat_type, seat_price = get_seat_type_and_price(seat_code, row_number, seat_letter)

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


@app.route("/results", methods=["GET", "POST"])
def results():
    if request.method == "POST":
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

        if not matching_flights:
            flash("No exact matches found. Showing sample flights instead.", "info")
            matching_flights = SAMPLE_FLIGHTS

        session["search_data"] = search_data
        session["last_flights"] = matching_flights

        return render_template(
    "results.html",
    flights=matching_flights,
    search_data=search_data,
    class_benefits=CLASS_BENEFITS,
    t=get_translation()
)

    search_data = session.get("search_data")
    matching_flights = session.get("last_flights")

    if not search_data or not matching_flights:
        flash("Please search for flights first.", "error")
        return redirect(url_for("home"))

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
            seat_sections = generate_seat_map(selected_flight)
            return render_template(
                "seat_selection.html",
                flight=selected_flight,
                seat_sections=seat_sections
            )

        booked_seats = get_booked_seats_for_flight(selected_flight)
        flight_date = session.get("search_data", {}).get("depart_date", "")
        random_unavailable = generate_seeded_unavailable_seats(
            selected_flight,
            flight_date,
            booked_seats
        )
        all_unavailable = booked_seats.union(random_unavailable)

        if selected_seat in all_unavailable:
            flash("That seat is no longer available. Please choose another seat.", "error")
            seat_sections = generate_seat_map(selected_flight)
            return render_template(
                "seat_selection.html",
                flight=selected_flight,
                seat_sections=seat_sections
            )

        session["selected_seat"] = selected_seat
        return redirect(url_for("review_booking"))

    seat_sections = generate_seat_map(selected_flight)
    return render_template(
        "seat_selection.html",
        flight=selected_flight,
        seat_sections=seat_sections
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


def calculate_price(selected_flight, extras):
    base_fare = selected_flight["price"]

    baggage_price = 0
    if "1 checked bag" in extras.get("baggage", ""):
        baggage_price = 30
    elif "2 checked bags" in extras.get("baggage", ""):
        baggage_price = 60

    insurance_price = 25 if "Insurance" in extras.get("insurance", "") else 0
    total_price = base_fare + baggage_price + insurance_price

    return {
        "base_fare": base_fare,
        "baggage_price": baggage_price,
        "insurance_price": insurance_price,
        "total_price": total_price
    }


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

    price_data = calculate_price(selected_flight, extras)

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
                extras=extras,
                **price_data
            )

        if not all(payment_data.values()):
            flash("Please fill in all payment fields.", "error")
            return render_template(
                "payment.html",
                flight=selected_flight,
                passenger=passenger_data,
                selected_seat=selected_seat,
                extras=extras,
                **price_data
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
                requested_date,
                requested_departure_airport,
                requested_departure_city,
                requested_departure_code,
                requested_destination_airport,
                requested_destination_city,
                requested_destination_code
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            "",
            "",
            "",
            "",
            "",
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
        extras=extras,
        **price_data
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
        points_earned=points_earned,
        extras=session.get("extras", {})
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

    requested_departure = request.form.get("requested_departure", "").strip()
    requested_destination = request.form.get("requested_destination", "").strip()
    requested_date = request.form.get("requested_date", "").strip()
    request_reason = request.form.get("request_reason", "").strip()

    if not requested_departure and not requested_destination and not requested_date and not request_reason:
        flash("Please enter at least one change request detail.", "error")
        return redirect(url_for("bookings"))

    departure_airport = parse_airport_selection(requested_departure) if requested_departure else None
    destination_airport = parse_airport_selection(requested_destination) if requested_destination else None

    if requested_departure and not departure_airport:
        flash("Please select a valid departure airport from the suggestions.", "error")
        return redirect(url_for("bookings"))

    if requested_destination and not destination_airport:
        flash("Please select a valid destination airport from the suggestions.", "error")
        return redirect(url_for("bookings"))

    route_summary_parts = []
    if departure_airport:
        route_summary_parts.append(f"{departure_airport['name']} ({departure_airport['code']})")
    if destination_airport:
        route_summary_parts.append(f"{destination_airport['name']} ({destination_airport['code']})")

    requested_route_summary = " to ".join(route_summary_parts) if route_summary_parts else "No route specified"

    request_summary = (
        f"Requested Route: {requested_route_summary} | "
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
            requested_date = ?,
            requested_departure_airport = ?,
            requested_departure_city = ?,
            requested_departure_code = ?,
            requested_destination_airport = ?,
            requested_destination_city = ?,
            requested_destination_code = ?
        WHERE id = ? AND user_id = ?
    """, (
        request_summary,
        "Pending",
        requested_route_summary,
        requested_date,
        departure_airport["name"] if departure_airport else "",
        departure_airport["city"] if departure_airport else "",
        departure_airport["code"] if departure_airport else "",
        destination_airport["name"] if destination_airport else "",
        destination_airport["city"] if destination_airport else "",
        destination_airport["code"] if destination_airport else "",
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


def get_currency_name_from_pycountry(code):
    currency = pycountry.currencies.get(alpha_3=code)
    if currency and getattr(currency, "name", None):
        return currency.name
    return code


def get_currency_symbol_for_code(code):
    symbols = {
        "GBP": "£",
        "USD": "$",
        "EUR": "€",
        "TRY": "₺",
        "AED": "د.إ",
        "CAD": "$",
        "AUD": "$",
        "NZD": "$",
        "JPY": "¥",
        "CNY": "¥",
        "INR": "₹",
        "IRR": "﷼",
        "RUB": "₽",
        "KRW": "₩",
        "THB": "฿",
        "CHF": "CHF",
        "SEK": "kr",
        "NOK": "kr",
        "DKK": "kr",
        "SAR": "﷼",
        "QAR": "﷼",
        "KWD": "د.ك",
        "BHD": ".د.ب",
        "OMR": "﷼",
    }
    return symbols.get(code, "")


def build_currency_metadata():
    rates = get_exchange_rates()
    available_codes = sorted(rates.keys())

    currency_to_territories = {}

    for country in list(pycountry.countries):
        alpha2 = getattr(country, "alpha_2", None)
        if not alpha2:
            continue

        try:
            currencies = get_territory_currencies(alpha2)
        except Exception:
            currencies = []

        for currency_code in currencies:
            currency_to_territories.setdefault(currency_code, []).append(country)

    available_currencies = []

    for code in available_codes:
        aliases = set()
        name = get_currency_name_from_pycountry(code)
        symbol = get_currency_symbol_for_code(code)

        aliases.add(normalize_search_text(code))
        aliases.add(normalize_search_text(name))

        for token in normalize_search_text(name).split():
            aliases.add(token)

        if symbol:
            aliases.add(normalize_search_text(symbol))

        for country in currency_to_territories.get(code, []):
            country_name = getattr(country, "name", "")
            official_name = getattr(country, "official_name", "")
            common_name = getattr(country, "common_name", "")
            alpha2 = getattr(country, "alpha_2", "")
            alpha3 = getattr(country, "alpha_3", "")

            for value in [country_name, official_name, common_name, alpha2, alpha3]:
                normalized = normalize_search_text(value)
                if normalized:
                    aliases.add(normalized)
                    for token in normalized.split():
                        aliases.add(token)

            for extra_alias in COUNTRY_NAME_ALIASES.get(alpha2, []):
                aliases.add(normalize_search_text(extra_alias))

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


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)