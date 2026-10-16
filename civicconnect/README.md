# CivicConnect - AI-Enabled Civic Issue Reporting System

A complete, demo-ready full-stack civic issue reporting web application with FastAPI backend, SQLite database, HTML/CSS/JS frontend, Leaflet maps, and AI image classification demo module.

## Features

- **Citizen Portal**: Report civic issues with photos, location, and description
- **Interactive Map**: View all issues on a Leaflet.js-powered OpenStreetMap
- **Community Support**: Upvote issues to increase priority
- **AI Image Classification**: Mock AI module suggests issue categories from photos
- **Duplicate Detection**: Location-based duplicate issue detection
- **Admin Dashboard**: Manage issues, assign departments, track resolution
- **Analytics**: View statistics by category and department
- **Real-time Notifications**: Get notified about issue status changes
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Backend**: Python FastAPI, SQLAlchemy, SQLite
- **Authentication**: JWT with bcrypt password hashing
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Maps**: Leaflet.js with OpenStreetMap
- **Images**: Pillow for image handling

## Project Structure

```
civicconnect/
├── backend/
│   ├── database.py       # SQLAlchemy models & demo data
│   ├── main.py           # FastAPI application with REST routes
│   ├── requirements.txt  # Python dependencies
│   └── uploads/          # Photo storage directory
├── frontend/
│   ├── index.html        # Landing page
│   ├── login.html        # Citizen login
│   ├── register.html     # Citizen registration
│   ├── report.html       # Report new issue
│   ├── browse.html       # Browse all issues
│   ├── issue.html        # Issue details page
│   ├── track.html        # Track complaint by ID
│   ├── map.html          # Interactive map view
│   ├── dashboard.html    # Citizen dashboard
│   ├── admin.html        # Admin dashboard
│   ├── admin-issues.html # Admin issue management
│   ├── analytics.html    # Analytics & statistics
│   ├── css/style.css     # Main stylesheet
│   └── js/               # JavaScript modules
│       ├── api.js        # API helper functions
│       ├── auth.js       # Authentication handling
│       ├── main.js       # Global navigation
│       ├── dashboard.js  # Citizen dashboard logic
│       ├── browse.js     # Browse issues logic
│       ├── map.js        # Map initialization
│       ├── report.js     # Issue reporting logic
│       ├── issue.js      # Issue details logic
│       ├── track.js      # Track complaint logic
│       ├── admin.js      # Admin dashboard logic
│       ├── admin-issues.js # Admin issue management
│       └── analytics.js  # Analytics logic
└── README.md
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd civicconnect/backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the server:
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`
   API documentation at `http://localhost:8000/docs`

### Frontend

The frontend is static HTML/CSS/JS. Simply open `frontend/index.html` in your browser, or serve it with any static file server.

## Demo Credentials

### Admin Account
- **Email**: admin@civicconnect.com
- **Password**: admin123

### Citizen Accounts
- **Email**: john@civicconnect.com | **Password**: password123
- **Email**: jane@civicconnect.com | **Password**: password123
- **Email**: mike@civicconnect.com | **Password**: password123
- **Email**: sarah@civicconnect.com | **Password**: password123
- **Email**: david@civicconnect.com | **Password**: password123

## Complaint ID Format

All complaints are assigned IDs in the format: `CC-1001`, `CC-1002`, etc.

## Priority Levels

- Low
- Medium
- High
- Critical

## Status Flow

Reported → Verified → In Progress → Resolved

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get access token

### Issues
- `GET /api/issues` - List all issues (with filters)
- `GET /api/issues/{id}` - Get issue details
- `POST /api/issues` - Create new issue
- `PUT /api/issues/{id}` - Update issue
- `DELETE /api/issues/{id}` - Delete issue (admin)
- `POST /api/issues/{id}/support` - Upvote/support issue
- `GET /api/issues/{id}/supports` - Get support count
- `POST /api/issues/{id}/feedback` - Submit feedback

### AI Classification
- `POST /api/ai/classify` - Mock AI image classification

### Admin
- `GET /api/admin/stats` - Dashboard statistics
- `GET /api/admin/issues` - All issues for management
- `PUT /api/admin/issues/{id}/assign` - Assign to department
- `PUT /api/admin/issues/{id}/resolve` - Mark as resolved

### Notifications
- `GET /api/notifications` - Get user notifications
- `PUT /api/notifications/{id}/read` - Mark as read

### User
- `GET /api/user/me` - Current user profile
- `GET /api/user/issues` - User's reported issues

## Demo Flow

1. **Citizen Login**: Login as john@civicconnect.com / password123
2. **Report Issue**: Go to Report Issue, fill in details, upload a photo
3. **AI Classification**: Upload a photo to see AI-suggested category and severity
4. **Community Support**: Browse issues and upvote important ones
5. **Admin Review**: Login as admin, verify and assign issues to departments
6. **Resolution**: Mark issues as resolved, citizens confirm with feedback
7. **Analytics**: View statistics on the admin dashboard

## License

MIT License - CivicConnect Project