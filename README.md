# AirGo Flight Booking System

University group project flight booking web application built with Flask and SQLite.

---

## Setup Instructions

### 1. Create virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize database
```bash
python init_db.py
```

This will create:
- Users, bookings, and flights tables
- Admin user: `admin@airgo.com`
- Default password is `admin123` for local development only
- For production, set AIRGO_ADMIN_PASSWORD environment variable
- 6 sample flights
- Performance indexes

### 4. Run the application
```bash
python app.py
```

Application will be available at: **http://localhost:5000**

### 5. Run tests
```bash
python -m pytest test_app.py -v
```

---

## API Endpoints

### Public API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/flights` | `GET` | List all available flights |
| `/api/flights/<flight_id>` | `GET` | Get single flight details |

### Authenticated User API (requires login)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/bookings` | `GET` | Get current user's bookings |
| `/api/bookings/<booking_id>` | `GET` | Get single booking details |
| `/api/bookings/<booking_id>` | `DELETE` | Cancel booking |

### Admin API (admin only)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/reports/bookings-per-flight` | `GET` | Booking counts per flight route |
| `/api/admin/reports/popular-routes` | `GET` | Top 10 most booked routes |
| `/api/admin/reports/peak-booking-times` | `GET` | Bookings by hour of day |

All API responses follow this format:
```json
{
  "data": [ ... ],
  "error": null
}
```

---

## Backend/API/Database contribution

This contribution implements:

### ✅ Database Improvements
1. **New `flights` table** - flights migrated from hardcoded Python list to database
2. **Foreign key constraints** enabled and enforced for `bookings.user_id`
3. **Performance indexes**:
   - `idx_bookings_user_id`
   - `idx_bookings_reference`
4. **Database initialization script** for clean setup
5. **Backward compatible** - all existing templates and routes work unchanged

### ✅ JSON API Endpoints
1. 5 new REST API endpoints for flights and bookings
2. Proper authentication and ownership checks
3. Standard JSON response format
4. Correct HTTP status codes (200, 401, 403, 404)
5. No breaking changes to existing HTML interface

### ✅ Admin Reporting
1. 3 new admin analytics endpoints
2. Booking counts per flight
3. Most popular routes ranking
4. Peak booking time analysis

### ✅ Tests
1. Added 10 new tests for all API endpoints
2. Fixed test teardown foreign key issues
3. 64 total tests covering all functionality