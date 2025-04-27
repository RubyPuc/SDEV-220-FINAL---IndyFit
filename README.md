# IndyFit

A gamified fitness application for Indianapolis Parks, encouraging healthy activities through social engagement and friendly competition.

## 📋 Project Overview

IndyFit is a web application designed to help Indianapolis residents engage with local parks through fitness activities. The app allows users to log workouts, earn points, and compete with other community members.

## ✨ Features

- **Activity Tracking**: Log workouts performed at Indianapolis park locations
- **Point System**: Earn points based on activity type and duration
- **User Profiles**: View personal activity history and points
- **Leaderboard**: See how you rank against other community members
- **Park Information**: Browse details about local parks and facilities

## 🛠️ Technology Stack

- Python (Backend)
- Flask (Web Framework)
- SQLite/SQLAlchemy (Database)
- HTML/CSS/JavaScript (Frontend)
- Docker & Docker Compose (Containerization)
- GitHub for version control

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository
```bash
git clone https://github.com/RubyPuc/SDEV-220-FINAL---IndyFit.git
cd SDEV-220-FINAL---IndyFit
```

2. Build and run the Docker containers
```bash
docker-compose up --build
```

3. Access the application
   - Open your browser and navigate to http://localhost:5000
   - Register a new user account at http://localhost:5000/register
   - Login as a user at http://localhost:5000/login
   - View your profile at http://localhost:5000/profile
   - Admin login is available at http://localhost:5000/admin/login
   - Default admin credentials:
     - Username: admin
     - Password: changeme123 (change this in production!)

## 🗂️ Project Structure

```
IndyFit/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── models/                # Database models
│   ├── __init__.py        # Package initialization
│   └── user.py            # User model with admin functionality
├── templates/             # HTML templates
│   ├── index.html         # Homepage template
│   ├── register.html      # User registration page
│   ├── user_login.html    # User login page
│   ├── profile.html       # User profile page
│   ├── login.html         # Admin login page
│   └── admin_dashboard.html # Admin dashboard
├── static/                # Static files
│   └── style.css          # Main stylesheet
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── CHANGELOG.md           # Detailed change history
└── README.md              # Project documentation
```

## 👨‍💻 Team Members

- Paul Sommers
- Roberth Pucajuria
- Andrew McKasson

## 📝 Development Plan

1. ✅ Set up project structure and environment
2. ✅ Implement admin user creation and authentication
3. ✅ Implement regular user registration and authentication
4. Create database models for activities and parks
5. Develop activity tracking functionality
6. Implement point system and leaderboard
7. Add park information and details
8. Enhance UI/UX with responsive design


## 📄 License

placeholder

---

*This project is being developed as part of the SDEV 220 course at Ivy Tech Community College.*