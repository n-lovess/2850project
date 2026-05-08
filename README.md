# ✈️ AirGo Flight Booking System

<div align="center">

## COMP2850 Software Engineering Group Project  
### University of Leeds – School of Computing

A full-stack flight booking web application developed using **Flask**, **SQLite**, and modern software engineering practices.

Designed to support airline customers and administrators through an intuitive booking platform, secure backend architecture, and data-driven management tools.

---

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey)
![Pytest](https://img.shields.io/badge/Pytest-Tested-green)
![License](https://img.shields.io/badge/License-Educational-orange)

</div>

---

# 📖 Table of Contents

- [Project Overview](#-project-overview)
- [Project Objectives](#-project-objectives)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Database Design](#-database-design)
- [API Documentation](#-api-documentation)
- [Authentication & Security](#-authentication--security)
- [Testing Strategy](#-testing-strategy)
- [Setup Instructions](#-setup-instructions)
- [Running the Application](#-running-the-application)
- [Project Structure](#-project-structure)
- [Software Engineering Practices](#-software-engineering-practices)
- [Accessibility & UX Considerations](#-accessibility--ux-considerations)
- [Future Improvements](#-future-improvements)
- [Contributors](#-contributors)
- [License](#-license)

---

# 🚀 Project Overview

AirGo is a web-based flight booking management system developed as part of the **COMP2850 Software Engineering Group Project** at the University of Leeds.

The application was designed around the project specification requirements and developed using iterative software engineering principles including:

- Requirements gathering
- User stories and personas
- Agile sprint planning
- UX/UI iteration
- Automated testing
- Database normalisation
- API development
- Version control with GitHub

The system allows airline customers to search and manage bookings while also providing administrative reporting and analytics tools for airline staff.

---

# 🎯 Project Objectives

The project was developed to satisfy the three core specification areas:

## 1. Booking System
A customer-facing platform allowing users to:

- Search for flights
- View available routes
- Book flights
- Manage reservations
- Review booking details

---

## 2. Management System
Administrative functionality enabling staff to:

- Track reservations
- Analyse booking data
- Monitor popular routes
- Generate booking reports
- View flight activity statistics

---

## 3. User Interaction System
Features supporting customer interaction workflows:

- Booking cancellation
- Reservation management
- Account-based access control
- Request processing support

---

# ✨ Key Features

## 👤 Customer Features

### Flight Search
Users can search flights using:
- Departure airport
- Destination airport
- Travel date
- Passenger information

### Booking Management
Authenticated users can:
- View their reservations
- Access booking details
- Cancel bookings
- Track booking references

### Reservation Access
Secure ownership validation ensures users can only access their own reservations.

---

## 🛠️ Administrative Features

### Reporting Dashboard APIs
Admin users can generate analytics including:
- Bookings per flight
- Most popular routes
- Peak booking times
- Reservation activity analysis

### Flight Management Support
The backend supports:
- Flight availability tracking
- Reservation analytics
- Booking data management

---

## ⚙️ Backend Features

- REST-style JSON API
- SQLite relational database
- Foreign key enforcement
- Authentication middleware
- Structured API responses
- Performance indexing
- Automated testing suite

---

# 🏗️ System Architecture

The system follows a layered web application architecture:

```text
Client Browser
      ↓
Flask Routes / Controllers
      ↓
Business Logic Layer
      ↓
SQLite Database
```

This architecture improves:
- Maintainability
- Separation of concerns
- Scalability
- Backend extensibility
- Testability

---

# 💻 Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Core backend programming |
| Flask | Web framework |
| SQLite | Relational database |
| HTML5 | Frontend markup |
| CSS3 | Styling and layout |
| Jinja2 | Server-side templating |
| Pytest | Automated testing |
| Git & GitHub | Version control and collaboration |

---

# 🗄️ Database Design

The application uses SQLite with a relational database structure.

## Core Tables

| Table | Purpose |
|------|---------|
| users | Stores registered users |
| flights | Stores flight information |
| bookings | Stores booking records |

---

## Database Improvements

The backend implementation introduced several improvements:

### Flights Table Migration
Flights were migrated from a hardcoded Python list into a fully relational database structure.

### Foreign Key Enforcement
Foreign key constraints were enabled and enforced for:
- `bookings.user_id`
- relational integrity protection

### Performance Optimisation
Indexes added:
```text
idx_bookings_user_id
idx_bookings_reference
```

These indexes improve:
- Booking lookup speed
- Query performance
- Reservation retrieval efficiency

### Initialisation Script
A dedicated setup script automatically:
- Creates database tables
- Inserts sample flight data
- Configures indexes
- Creates admin accounts

---

# 🔌 API Documentation

The system exposes REST-style API endpoints.

---

# 🌍 Public API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/flights` | GET | Retrieve all flights |
| `/api/flights/<flight_id>` | GET | Retrieve flight details |

---

# 🔐 Authenticated User API

Requires login authentication.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/bookings` | GET | Retrieve current user bookings |
| `/api/bookings/<booking_id>` | GET | Retrieve booking details |
| `/api/bookings/<booking_id>` | DELETE | Cancel booking |

### Security Features
- Ownership validation
- Session authentication
- Access restriction checks

---

# 👨‍💼 Admin API

Admin-only reporting endpoints.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/reports/bookings-per-flight` | GET | Booking counts per flight |
| `/api/admin/reports/popular-routes` | GET | Top booked routes |
| `/api/admin/reports/peak-booking-times` | GET | Booking frequency by hour |

---

# 📦 JSON Response Format

All endpoints return structured JSON responses.

## Successful Response

```json
{
  "data": [],
  "error": null
}
```

## Error Response Example

```json
{
  "data": null,
  "error": "Booking not found"
}
```

---

# 🔒 Authentication & Security

The application includes several security and validation measures.

## Authentication
- Session-based login system
- Authenticated API access
- Admin role protection

## Validation
- Booking ownership checks
- Input validation
- Graceful exception handling
- Foreign key enforcement

## HTTP Status Codes
The API correctly returns:
- `200 OK`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

# 🧪 Testing Strategy

The project includes automated backend and API testing using **Pytest**.

---

# ✅ Test Coverage

The test suite covers:
- Flight API endpoints
- Booking workflows
- Authentication checks
- Admin analytics endpoints
- Database operations
- Error handling behaviour

---

# 📊 Testing Summary

| Metric | Value |
|--------|------|
| Total Tests | 64 |
| API Tests Added | 10 |
| Testing Framework | Pytest |
| Automated Testing | ✅ |
| Backend Validation Testing | ✅ |

---

# ⚡ Setup Instructions

---

## 1. Clone the Repository

```bash
git clone <repository-url>
cd airgo
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Initialise the Database

```bash
python init_db.py
```

This automatically creates:
- Users table
- Flights table
- Bookings table
- Performance indexes
- Sample flights
- Default admin account

---

# 👤 Default Administrator Account

```text
Email: admin@airgo.com
Password: admin123
```

⚠️ For production deployment, configure:

```text
AIRGO_ADMIN_PASSWORD
```

as an environment variable.

---

# ▶️ Running the Application

Start the Flask application:

```bash
python app.py
```

Application URL:

```text
http://localhost:5000
```

---

# 🧪 Running the Test Suite

```bash
python -m pytest test_app.py -v
```

---

# 📁 Project Structure

```text
airgo/
│
├── app.py
├── init_db.py
├── requirements.txt
├── test_app.py
│
├── templates/
│   ├── booking pages
│   ├── authentication pages
│   └── admin pages
│
├── static/
│   ├── css/
│   ├── js/
│   └── assets/
│
├── database/
│
└── README.md
```

---

# 🔄 Software Engineering Practices

The project followed modern software engineering workflows.

## Agile Development
- Sprint planning
- Weekly meetings
- Retrospectives
- Incremental development

## Git & GitHub Workflow
- Feature branches
- Pull requests
- Version control management
- Collaborative merging strategy

## Documentation
The wider project documentation includes:
- Personas
- Job stories
- User stories
- Meeting notes
- Retrospectives
- Wireframes
- Database diagrams
- Class diagrams
- UX feedback iterations

---

# ♿ Accessibility & UX Considerations

The user interface was designed with usability and accessibility in mind.

## UX Principles
- Consistent navigation
- Clear booking workflows
- Readable layouts
- Structured forms
- User-focused interactions

## Accessibility Considerations
- Clear visual hierarchy
- Accessible form inputs
- Consistent colour usage
- Responsive layout structure

The interface was iteratively improved through testing and feedback.

---

# 📈 Future Improvements

Potential future extensions include:

- Seat selection during booking
- Flight modification requests
- Email notifications
- Complaint submission forms
- Loyalty points system
- Interactive route visualisation
- Mobile-responsive redesign
- Admin dashboard interface
- Real-time flight availability updates

---

# 👥 Contributors

Developed as part of the:

## University of Leeds
### COMP2850 Software Engineering Group Project

---

# 📜 License

This project was developed for educational purposes as part of university coursework.

Not intended for commercial deployment.

---
